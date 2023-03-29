import os, time, platform
from app import cbmpycurator as CBCR
import cbmpy

__VERSION__ = '3.0'

cDir = os.path.dirname(os.path.abspath(os.sys.argv[0]))
try:
    if os.sys.argv[1].endswith('.xml'):
        MODEL_DIR, mfile = os.path.split(os.sys.argv[1])
    else:
        MODEL_DIR = os.sys.argv[1]
        mfile = None
except:
    # debugging hack
    print('{} does not seem to exist'.format(os.sys.argv[1]))

frog_curator = 'run-' + time.strftime('%m%d-%H%M')
frog_date = time.strftime('%Y-%m-%d')


def write_config(fpath, filename, frog_curator, frog_date, model_md5, model_sha256):
    if cbmpy.CBConfig.__CBCONFIG__['SOLVER_ACTIVE'] == 'CPLEX':
        try:
            solver_version = str(cbmpy.CBCPLEX.cplex.__version__)
        except:
            solver_version = "unknown"
        
    config = {
        "frog_date": frog_date,
        "frog_version": "0.1.2",
        "frog_curators": [frog_curator],
        "software": {
            "frog": {
                "name": "cbmpyweb offline-curator",
                "version": __VERSION__,
                "url": "https://osf.io/t6mh3"
            },
            "toolbox": {
                "name": "cbmpy",
                "version": str(cbmpy.__version__),
                "url": "https://systemsbioinformatics.github.io/cbmpy"
            },
            "solver": {
                "name": cbmpy.CBConfig.__CBCONFIG__['SOLVER_ACTIVE'],
                "version": solver_version
            }
        },
        "model_filename": filename,
        "model_md5": model_md5,
        "model_sha256": model_sha256,
        "environment": "{} {} ({})".format(platform.system(), platform.release(), platform.architecture()[0]),
    }

    fpath = os.path.join(fpath, 'metadata.json')
    import json
    with open(fpath, 'w') as F:
        json.dump(config, F, indent=' ')
    return

roundoff_num = 6
TOOL_ID = 'cbmpy'


write_config(MODEL_DIR, "", frog_curator, frog_date, "", "")

if mfile is None:
    model_files = [m for m in os.listdir(MODEL_DIR) if m.endswith('.xml')]
else:
    model_files = [mfile]

report = '# FBA Curation Report {} \n\n'.format(time.strftime('%Y-%m-%d-%H:%M'))

for m_ in model_files:
    print('\n\n#################\n# {}\n#################\n\n'.format(m_))

    report += '########################\n'
    report += '\nModel: {}\n'.format(m_)


    if m_.endswith('.xml'):
        RESULT_DIR = os.path.join(MODEL_DIR, 'result-{}'.format(m_[:-4]))
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    model_md5 = CBCR.hashFileMd5(os.path.join(MODEL_DIR, m_))
    model_sha256 = CBCR.hashFileSha256(os.path.join(MODEL_DIR, m_))
    import shutil



    if not os.path.exists(os.path.join(RESULT_DIR, 'metadata.json')):
        write_config(RESULT_DIR, m_, frog_curator, frog_date, model_md5, model_sha256)

    shutil.copyfile(os.path.join(MODEL_DIR, m_), os.path.join(RESULT_DIR, m_))

    print('\n# Using\n{}\n{}\n'.format(MODEL_DIR, RESULT_DIR))

    T0 = time.time()

    testmod = cbmpy.readSBML3FBC(os.path.join(MODEL_DIR, m_))
    testmod.setName(m_)

    T1 = time.time()
    report += 'Load model: {:.2f}s\n'.format(T1 - T0)

    # Test objective
    _ = CBCR.testObjective(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

    T2 = time.time()
    report += 'Test objective: {:.2f}s\n'.format(T2 - T1)

    # Test FVA
    _ = CBCR.testFVA(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

    T3 = time.time()
    report += 'Test FVA: {:.2f}s\n'.format(T3 - T2)

    # Test Gene Deletion
    _ = CBCR.testGeneDeletion(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

    T4 = time.time()
    report += 'Test gene deletions: {:.2f}s\n'.format(T4 - T3)

    # Test Reaction Deletion
    _ = CBCR.testReactionDeletion(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

    T5 = time.time()
    report += 'Test reaction deletions: {:.2f}s\n'.format(T5 - T4)
    report += 'Total time: {:.2f}s\n'.format(T5 - T0)

    # Add COMBINE archive stuff
    _ = CBCR.addCombineMetadata(MODEL_DIR, RESULT_DIR, m_, frog_curator)
    
    # create OMEX archive
    CBCR.f_create_omex(RESULT_DIR, RESULT_DIR, m_)

report += '\n########################\n'

#format(time.strftime('%Y-%m-%d-%H:%M')

with open(os.path.join(RESULT_DIR, 'curation-timings.txt'), 'w') as F:
    F.write(report)

print(report)


