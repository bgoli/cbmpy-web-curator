import os, time, json, hashlib, zipfile, math
import cbmpy

__VERSION__ = 1.0


# TODO TODO TODO # THIS NEEDS TO BE DONE VIA CONFIG
# multicore python bin hack

# if os.path.exists('c:\\Anaconda3\\envs\\flaskdev\\python.exe'):
#     cbmpy.__CBCONFIG__['MULTICORE_PYTHON_BIN_OVERRIDE'] = 'c:\\Anaconda3\\envs\\flaskdev\\python.exe'
# else:
#     cbmpy.__CBCONFIG__['MULTICORE_PYTHON_BIN_OVERRIDE'] = '/home/bolivier/frogg-app/venv/bin/python3'

cbmpy.__CBCONFIG__['MULTICORE_PYTHON_BIN_OVERRIDE'] = os.sys.executable

print('MULTICORE PATH {}'.format(cbmpy.__CBCONFIG__['MULTICORE_PYTHON_BIN_OVERRIDE']))


def hashFileMd5(fpath):
    md5_hash = hashlib.md5()
    a_file = open(fpath, 'rb')
    content = a_file.read()
    md5_hash.update(content)
    digest = md5_hash.hexdigest()
    print(digest)
    return digest

def hashFileSha256(fpath):
    sha_hash = hashlib.sha256()
    a_file = open(fpath, 'rb')
    content = a_file.read()
    sha_hash.update(content)
    digest = sha_hash.hexdigest()
    print(digest)
    return digest


def readMetadata(fpath):
    with open(os.path.join(fpath, 'metadata.json'), 'r') as F:
        metadata = json.load(F)
        print(metadata)
    return metadata


def writeMetadata(fname, fpath, metadata):
    F = open(os.path.join(fpath, fname), 'w')
    print(metadata)
    json.dump(metadata, F, indent=' ')
    F.close()


def addMetadata(pathin, pathout, model_file, curator_id):
    mdat = readMetadata(pathin)
    mdat['frog_curators'] = [curator_id]
    mdat['frog_date'] = time.strftime('%Y-%m-%d-%H-%M')
    mdat['frogg_sessionid'] = '{}-{}'.format(mdat['frog_curators'][0].lower().replace(' ', '-'), str(time.monotonic()).replace('.', '-'))
    mdat['model_filename'] = model_file
    mdat['model_md5'] = hashFileMd5(os.path.join(pathin, model_file))
    writeMetadata('metadata.json', pathout, mdat)
    return mdat


def addCombineMetadata(pathin, pathout, model_file, curator_id):
    with open(os.path.join(pathout, 'metadata.rdf'), 'w') as F:
        F.write(generateCOMBINEarchiveMetadata('CBMPy', curator_id))

    with open(os.path.join(pathout, 'manifest.xml'), 'w') as F:
        F.write(generateCombineArchiveManifest(pathin, pathout, model_file))


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

    #obj_func_value = ''
    #if m.SOLUTION_STATUS_INT == 1:
        #solution_status = 'optimal'
        #obj_func_value = round(m.getOptimalValue(), sigfig)
    #else:
        #solution_status = 'infeasible'
        #obj_func_value = ''


    # do FVA
    optPercentage = 100.0

    import multiprocessing
    
    multiprocessing.cpu_count

    if len(m.getReactionIds()) <= 1000:
        fvals, fids = cbmpy.doFVA(m, optPercentage=100.0)
    elif len(m.getReactionIds()) <= 3000:
        fvals, fids = cbmpy.CBMultiCore.runMultiCoreFVA(m, procs=8, override_bin=override_bin, optPercentage=100.0)
    else:
        fvals, fids = cbmpy.CBMultiCore.runMultiCoreFVA(m, procs=8, override_bin=override_bin, optPercentage=100.0)

    ridmap = m.getReactionIds()
    ridmap.sort()

    # set the "optimal" property where "optimal" is defined as, for each FVA evaluation, 
    # at least one of the two numerical optimizations succeeded. 
    for r in range(len(fids)):
        r = fids.index(ridmap[r])
        if fvals[r][5] == 1 or fvals[r][6] == 1:
            solution_status = 'optimal'
        else:
            solution_status = 'infeasible'

        # lets kill some nans
        lval = fvals[r][2]
        uval = fvals[r][3]
        if not math.isnan(lval):
            round(lval, sigfig)
        else:
            lval = ' '
        if not math.isnan(uval):
            round(uval, sigfig)
        else:
            uval = ' '

        output.append(
            [
                #mdata['software.name'],
                mod_name,
                m.getActiveObjective().getId(),
                fids[r],
                round(fvals[r][0], sigfig),
                solution_status,
                lval,
                uval,
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
    #mdata = readMetadata(os.path.split(result_path)[0])
    #if metadata is not None:
        #pass
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
        if not math.isnan(gene_dict[g_]):
            solution_status = 'optimal'
            value = round(gene_dict[g_], sigfig)
        else:
            solution_status = 'infeasible'
            value = ' '

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
        if math.isnan(output[-1][-1]):
            output[-1][-1] = ' '

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


def generateCombineArchiveManifest(in_dir, out_dir, model_file):
#     tsv_files = ['01_objective.tsv', '02_fva.tsv', '03_gene_deletion.tsv', '04_reaction_deletion.tsv']
#     mdat_files = ['curation-timings.txt', 'metadata.json', 'metadata.rdf']

    man_out = """<?xml version="1.0" encoding="UTF-8"?>
<omexManifest xmlns="http://identifiers.org/combine.specifications/omex-manifest">
 <content location="." format="https://identifiers.org/combine.specifications:omex"/>
 <content location="./manifest.xml" format="https://identifiers.org/combine.specifications:omex-manifest"/>\n"""

    if os.path.exists(out_dir):
        for f_ in os.listdir(out_dir):
            print(f_)
            if f_ == 'metadata.rdf':
                man_out += '<content location="./metadata.rdf" format="http://identifiers.org/combine.specifications/omex-metadata"/>\n'
            elif f_ == 'metadata.json':
                man_out += ' <content location="./metadata.json" format="https://identifiers.org/combine.specifications:frog-metadata-version-1"/>\n'
            elif f_ == 'curation-timings.txt':
                man_out += ' <content location="./curation-timings.txt" format="text/plain"/>\n'
            elif f_ == '01_objective.tsv':
                man_out += ' <content location="./01_objective.tsv" format="https://identifiers.org/combine.specifications:frog-objective-version-1"/>\n'
            elif f_ == '02_fva.tsv':
                man_out += ' <content location="./02_fva.tsv" format="https://identifiers.org/combine.specifications:frog-fva-version-1"/>\n'
            elif f_ == '03_gene_deletion.tsv':
                man_out += ' <content location="./03_gene_deletion.tsv" format="https://identifiers.org/combine.specifications:frog-genedeletion-version-1"/>\n'
            elif f_ == '04_reaction_deletion.tsv':
                man_out += ' <content location="./04_reaction_deletion.tsv" format="https://identifiers.org/combine.specifications:frog-reactiondeletion-version-1"/>\n'
    man_out += ' <content location="./{}" format="https://identifiers.org/combine.specifications:sbml" master="true"/>\n'.format(model_file)
    man_out += "</omexManifest>\n"
    return man_out

def generateCOMBINEarchiveMetadata(tool_name, creator):
    return """
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:vCard="http://www.w3.org/2006/vcard/ns#"
    xmlns:bqmodel="http://biomodels.net/models-qualifiers">
 <rdf:Description rdf:about=".">
 <dcterms:creator>
 <rdf:Bag>
  <rdf:li rdf:parseType="Resource">
   <vCard:hasName rdf:parseType="Resource">
    <vCard:family-name>{}</vCard:family-name>
    <vCard:given-name>{}</vCard:given-name>
   </vCard:hasName>
   <vCard:hasEmail rdf:resource="" />
   <vCard:organization-name>

   </vCard:organization-name>
  </rdf:li>
 </rdf:Bag>
 </dcterms:creator>
   <dcterms:created rdf:parseType="Resource">
    <dcterms:W3CDTF>{}</dcterms:W3CDTF>
   </dcterms:created>
   <dcterms:modified rdf:parseType="Resource">
    <dcterms:W3CDTF>{}</dcterms:W3CDTF>
   </dcterms:modified>
 </rdf:Description>
</rdf:RDF>
""".format(tool_name, creator, time.strftime('%Y-%m-%d %H:%M'), time.strftime('%Y-%m-%d %H:%M'))

def f_zip_results(zfpath, model):
    """
    Create a zip archive of the contents of zfpath
    """
    mpath, arcname = os.path.split(zfpath)
    arcname += '.zip'
    model = model.replace('result-','')

    print('#######################')
    print(zfpath)
    print(arcname)
    print(mpath)
    print(model)
    print('#######################')

    # adding combine stuff
    addCombineMetadata(zfpath, zfpath, model, 'Software')


    zf = zipfile.ZipFile(os.path.join(zfpath, arcname), mode='w', compression=zipfile.ZIP_DEFLATED)

    zf.write(os.path.join(mpath, model), model)

    for fn in os.listdir(zfpath):
        print(fn)
        if not fn.endswith('.zip'):
            zf.write(os.path.join(zfpath, fn), fn)
    zf.close()

def f_create_omex(in_dir, out_dir, model_file):
    """
    Create a omex archive of the contents of zfpath
    """
    arcname = model_file + '.omex'

    print('#######################')
    print(in_dir)
    print(out_dir)
    print(model_file)
    print(arcname)
    print('#######################')

    zf = zipfile.ZipFile(os.path.join(out_dir, arcname), mode='w', compression=zipfile.ZIP_DEFLATED)

    #print(os.listdir(in_dir))
    print(os.listdir(out_dir))
    for fn in os.listdir(out_dir):
        print(fn)
        if fn.endswith('.zip') or fn.endswith('.omex'):
            pass
        else:
            zf.write(os.path.join(out_dir, fn), fn)
    zf.close()
    print("\nOMEX: {}".format(os.path.join(out_dir, arcname)))



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
