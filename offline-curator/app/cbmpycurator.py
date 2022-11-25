import os, time, json, hashlib
import cbmpy

# TODO TODO TODO # THIS NEEDS TO BE DONE VIA CONFIG
# multicore python bin hack

if os.path.exists('c:\\Anaconda3\\envs\\flaskdev\\python.exe'):
    cbmpy.__CBCONFIG__['MULTICORE_PYTHON_BIN_OVERRIDE'] = 'c:\\Anaconda3\\envs\\flaskdev\\python.exe'
else:
    cbmpy.__CBCONFIG__['MULTICORE_PYTHON_BIN_OVERRIDE'] = '/home/bolivier/frogg-app/venv/bin/python3'
print('MULTICORE PATH {}'.format(cbmpy.__CBCONFIG__['MULTICORE_PYTHON_BIN_OVERRIDE']))


#{
 #"curator.name": "CBMPyWeb",
 #"curator.version": "0.3.0",
 #"curator.url": "http://curator.fame-vu.surf-hosted.nl:5000/",
 #"curator.date": "",
 #"curator.id": "",
 #"curator.sessionid": "",
 #"software.name": "cbmpy",
 #"software.version": "0.8.0",
 #"software.url": "https://github.com/SystemsBioinformatics/cbmpy",
 #"software.environment": "Linux 4.15.0-118-generic (64bit)",
 #"solver.name": "CPLEX",
 #"solver.version": "12.10.0.0",
 #"model.filename": "",
 #"model.md5": ""
#}

def hashFileMd5(fpath):
    md5_hash = hashlib.md5()
    a_file = open(fpath, 'rb')
    content = a_file.read()
    md5_hash.update(content)
    digest = md5_hash.hexdigest()
    print(digest)
    return digest

def readMetadata(fpath):
    with open(os.path.join(fpath, 'metadata.json'), 'r') as F:
        metadata = json.load(F)
        print(metadata)
    return metadata

def writeMetadata(fpath, metadata):
    F = open(os.path.join(fpath, 'metadata.json'), 'w')
    print(metadata)
    json.dump(metadata, F, indent=' ')
    F.close()

def addMetadata(pathin, pathout, model_file, curator_id):
    mdat = readMetadata(pathin)
    mdat['curator.id'] = curator_id
    mdat['curator.date'] = time.strftime('%Y-%m-%d-%H-%M')
    mdat['curator.sessionid'] = '{}-{}'.format(mdat['curator.name'].lower().replace(' ', '-'), str(time.monotonic()).replace('.', '-'))
    mdat['model.filename'] = model_file
    mdat['model.md5'] = hashFileMd5(os.path.join(pathin, model_file))
    writeMetadata(pathout, mdat)
    return mdat

def testObjective(m, result_path, tool_id, sigfig=6, metadata=None):
    report_name = '01_objective.tsv'
    head = ['software', 'model', 'objective', 'status', 'value']
    head = ['model', 'objective', 'status', 'value']
    output = [head]
    ##m = mod.clone()
    mod_name = m.getName()
    solution_status = ''

    print(os.path.split(result_path))
    mdata = readMetadata(os.path.split(result_path)[0])
    if metadata is not None:
        pass
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    cbmpy.doFBA(m)

    if m.SOLUTION_STATUS_INT == 1:
        solution_status = 'optimal'
        value = round(m.getOptimalValue(), sigfig)
    else:
        solution_status = 'infeasible'
        value = ''

    #output.append([mdata['software.name'], mod_name, m.getActiveObjective().getId(), solution_status, value])
    output.append([mod_name, m.getActiveObjective().getId(), solution_status, value])

    with open(os.path.join(result_path, report_name), 'w') as F:
        writeTSV(F, output)
    return output


def testFVA(m, result_path, tool_id, sigfig=6, metadata=None, override_bin=cbmpy.__CBCONFIG__['MULTICORE_PYTHON_BIN_OVERRIDE']):
    report_name = '02_fva.tsv'
    # head = ['model', 'objective', 'reaction', 'status', 'value', 'minimum', 'maximum']
    #head = ['software', 'model', 'objective', 'reaction', 'objValue', 'status', 'minimum', 'maximum']
    head = ['model', 'objective', 'reaction', 'flux', 'status', 'minimum', 'maximum', 'fraction_optimum']
    output = [head]
    #m = mod.clone()
    mod_name = m.getName()
    solution_status = 'None'

    print(os.path.split(result_path))
    mdata = readMetadata(os.path.split(result_path)[0])
    if metadata is not None:
        pass
    if not os.path.exists(result_path):
        os.makedirs(result_path)
        
    # get the current obj value for output
    cbmpy.doFBA(m)

    obj_func_value = ''
    if m.SOLUTION_STATUS_INT == 1:
        solution_status = 'optimal'
        obj_func_value = round(m.getOptimalValue(), sigfig)
    else:
        solution_status = 'infeasible'
        obj_func_value = ''


    # do FVA
    optPercentage = 100.0
    
    if len(m.getReactionIds()) <= 1000:
        fvals, fids = cbmpy.doFVA(m, optPercentage=100.0)
    elif len(m.getReactionIds()) <= 3000:
        fvals, fids = cbmpy.CBMultiCore.runMultiCoreFVA(m, procs=6, override_bin=override_bin, optPercentage=100.0)
    else:
        fvals, fids = cbmpy.CBMultiCore.runMultiCoreFVA(m, procs=6, override_bin=override_bin, optPercentage=100.0)

    ridmap = m.getReactionIds()
    ridmap.sort()

    for r in range(len(fids)):
        r = fids.index(ridmap[r])
        if fvals[r][5] == 1 or fvals[r][6] == 1:
            solution_status = 'optimal'
        else:
            solution_status = 'infeasible'

        output.append(
            [
                #mdata['software.name'],
                mod_name,
                m.getActiveObjective().getId(),
                fids[r],
                # my first choice is the flux value, but apparently the obj function value should be output
                # round(fvals[r][0], sigfig),
                obj_func_value,
                solution_status,
                round(fvals[r][2], sigfig),
                round(fvals[r][3], sigfig),
                optPercentage/100.0
            ]
        )

    with open(os.path.join(result_path, report_name), 'w') as F:
        writeTSV(F, output)
    return output


def testGeneDeletion(m, result_path, tool_id, sigfig=6, metadata=None):
    report_name = '03_gene_deletion.tsv'
    #head = ['software', 'model', 'objective', 'gene', 'status', 'value']
    head = ['model', 'objective', 'gene', 'status', 'value']
    output = [head]
    #m = mod.clone()
    mod_name = m.getName()
    # mod_name = m.getId()
    solution_status = 'optimal'

    print(os.path.split(result_path))
    mdata = readMetadata(os.path.split(result_path)[0])
    if metadata is not None:
        pass
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    res = cbmpy.CBCPLEX.cplx_singleGeneScan(
        m, r_off_low=0.0, r_off_upp=0.0, optrnd=sigfig, altout=False
    )

    gene_dict = {}
    for r_ in res:
        if r_[0] != 'wt':
            gene_dict[m.getGene(r_[0]).getLabel()] = r_[1]
    gidx = list(gene_dict.keys())
    gidx.sort()
    for g_ in gidx:
        import math

        if not math.isnan(gene_dict[g_]):
            solution_status = 'optimal'
            value = round(gene_dict[g_], sigfig)
        else:
            solution_status = 'infeasible'
            #value = ''

        output.append(
            #[mdata['software.name'], mod_name, m.getActiveObjective().getId(), g_, solution_status, value]
            [mod_name, m.getActiveObjective().getId(), g_, solution_status, value]
        )

    with open(os.path.join(result_path, report_name), 'w') as F:
        writeTSV(F, output)
    return output


def testReactionDeletion(m, result_path, tool_id, sigfig=6, metadata=None):
    report_name = '04_reaction_deletion.tsv'
    #head = ['software', 'model', 'objective', 'reaction', 'status', 'value']
    head = ['model', 'objective', 'reaction', 'status', 'value']
    output = [head]
    #m = mod.clone()
    mod_name = m.getName()

    print(os.path.split(result_path))
    mdata = readMetadata(os.path.split(result_path)[0])
    if metadata is not None:
        pass
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    res = cbmpy.CBCPLEX.cplx_singleReactionDeletionScan(
        m, r_off_low=0.0, r_off_upp=0.0, optrnd=sigfig
    )

    rkeys = list(res.keys())
    rkeys.sort()

    for r in rkeys:
        output.append(
            [
                #mdata['software.name'],
                mod_name,
                m.getActiveObjective().getId(),
                r,
                res[r]['status'],
                res[r]['opt'],
            ]
        )
        #if math.isnan(output[-1][-1]):
            #output[-1][-1] = ''

    with open(os.path.join(result_path, report_name), 'w') as F:
        writeTSV(F, output)
    return output


def testReactionDeletionLegacy(m, result_path, tool_id, sigfig=6, metadata=None):
    report_name = '04_reaction_deletion.tsv'
    head = ['software', 'model', 'objective', 'reaction', 'status', 'value']
    output = [head]
    #m = mod.clone()
    mod_name = m.getName()
    solution_status = 'optimal'

    print(os.path.split(result_path))
    mdata = readMetadata(os.path.split(result_path)[0])
    if metadata is not None:
        pass
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    ridx = m.getReactionIds()
    ridx.sort()
    cbmpy.doFBA(m)
    for r_ in ridx:
        R = m.getReaction(r_)
        R.deactivateReaction()
        cbmpy.doFBA(m, build_n=False, quiet=True)
        R.reactivateReaction()
        if m.SOLUTION_STATUS_INT == 1:
            solution_status = 'optimal'
            value = round(m.getOptimalValue(), sigfig)
        else:
            solution_status = 'infeasible'
            value = ''

        output.append(
            [mdata['software.name'], mod_name, m.getActiveObjective().getId(), r_, solution_status, value]
        )

    with open(os.path.join(result_path, report_name), 'w') as F:
        writeTSV(F, output)
    return output


def writeTSV(f, data):
    for r_ in data:
        for c_ in range(len(r_)):
            if c_ + 1 != len(r_):
                f.write('{}\t'.format(r_[c_]))
            else:
                f.write('{}\n'.format(r_[c_]))


if __name__ == '__main__':
    # moving this into a separate offline runner outside of app - bgoli 
    cDir = os.path.dirname(os.path.abspath(os.sys.argv[0]))


    MODEL_DIR, mfile = os.path.split(os.sys.argv[1])
    RESULT_DIR = os.path.join(MODEL_DIR, 'result-{}'.format(mfile))
    roundoff_num = 6
    TOOL_ID = 'cbmpy'


    print(mfile)
    print(MODEL_DIR)
    print(RESULT_DIR)
    model_files = [mfile]


    # model_files = ['e_coli_core.xml', 'iAB_AMO1410_SARS-CoV-2.xml', 'iJR904.xml.gz']
    # model_files = ['e_coli_core.xml']
    #MODEL_DIR = os.path.abspath(
        #'d:\\Development\\mypython\\cbmpydev\\fbc_curation\\examples\\models'
    #)
    #RESULT_DIR = os.path.abspath(
        #'d:\\Development\\mypython\\cbmpydev\\fbc_curation\\examples\\Results'
    #)

    print('\n# Using\n{}\n{}\n'.format(MODEL_DIR, RESULT_DIR))

    report = '# FBA Curation Report {} \n\n'.format(time.strftime('%Y-%m-%d-%H:%M'))

    for m_ in model_files:

        print('\n\n#################\n# {}\n#################\n\n'.format(m_))

        report += '########################\n'
        report += '\nModel: {}\n'.format(m_)

        T0 = time.time()

        testmod = cbmpy.readSBML3FBC(os.path.join(MODEL_DIR, m_))
        testmod.setName(m_)

        T1 = time.time()
        report += 'Load model: {:.2f}s\n'.format(T1 - T0)

        # Test objective
        _ = testObjective(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

        T2 = time.time()
        report += 'Test objective: {:.2f}s\n'.format(T2 - T1)

        # Test FVA
        _ = testFVA(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

        T3 = time.time()
        report += 'Test FVA: {:.2f}s\n'.format(T3 - T2)

        # Test Gene Deletion
        _ = testGeneDeletion(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

        T4 = time.time()
        report += 'Test gene deletions: {:.2f}s\n'.format(T4 - T3)

        # Test Reaction Deletion
        _ = testReactionDeletion(
            testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num
        )

        T5 = time.time()
        report += 'Test reaction deletions: {:.2f}s\n'.format(T5 - T4)
        report += 'Total time: {:.2f}s\n'.format(T5 - T0)

    report += '\n########################\n'

    #format(time.strftime('%Y-%m-%d-%H:%M')

    with open(
        os.path.join(RESULT_DIR, 'curation-timings.txt'), 'w'
    ) as F:
        F.write(report)

    print(report)
