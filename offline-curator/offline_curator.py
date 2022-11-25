import os, time, platform
from app import cbmpycurator as CBCR
import cbmpy

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
    

def write_config(fpath, filename):
    config = {
     "curator.name": "CBMPyWEB offline-curator",
     "curator.version": "0.1",
     "curator.url": "",
     "curator.date": "",
     "curator.id": "",
     "curator.sessionid": "",
     "software.name": "cbmpy",
     "software.version": str(cbmpy.__version__),
     "software.url": "https://github.com/SystemsBioinformatics/cbmpy",
     "software.environment": "{} {} ({})".format(platform.system(), platform.release(), platform.architecture()[0]),
     "solver.name": "cbmpy",
     "solver.version": "0.2",
     "model.filename": "{}".format(filename),
     "model.md5": "" }
    fpath = os.path.join(fpath, 'metadata.json')
    import json
    with open(fpath, 'w') as F:
        json.dump(config, F, indent=' ')
    return

roundoff_num = 6
TOOL_ID = 'cbmpy'


write_config(MODEL_DIR, "")

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
    
    
    if not os.path.exists(os.path.join(RESULT_DIR, 'metadata.json')):
        write_config(RESULT_DIR, m_)

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

report += '\n########################\n'

#format(time.strftime('%Y-%m-%d-%H:%M')

with open(os.path.join(RESULT_DIR, 'curation-timings.txt'), 'w') as F:
    F.write(report)

print(report)


