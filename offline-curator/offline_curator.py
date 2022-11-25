import os, time
from app import cbmpycurator as R
import cbmpy

cDir = os.path.dirname(os.path.abspath(os.sys.argv[0]))
try:
    MODEL_DIR, mfile = os.path.split(os.sys.argv[1])
except:
    # debugging hack
    print('{} does not seem to exist'.format(MODEL_DIR))
    
    #MODEL_DIR, mfile = os.path.split(os.path.abspath('d:\\Development\\cbmpy-web-curator\\test-models\\VvuMBEL943_2022.xml'))
    

def write_config(fpath):
    config = {
     "curator.name": "CBMPyFROGG",
     "curator.version": "0.7.9",
     "curator.url": "",
     "curator.date": "",
     "curator.id": "",
     "curator.sessionid": "",
     "software.name": "cbmpy",
     "software.version": str(cbmpy.__version__),
     "software.url": "https://github.com/SystemsBioinformatics/cbmpy",
     "software.environment": "Windows 10 (64bit)",
     "solver.name": "cbmpy",
     "solver.version": "0.2",
     "model.filename": "",
     "model.md5": "" }
    fpath = os.path.join(fpath, 'metadata.json')
    import json
    with open(fpath, 'w') as F:
        json.dump(config, F)
    return

if not os.path.exists(os.path.join(MODEL_DIR, 'metadata.json')):
    write_config(MODEL_DIR)
    

RESULT_DIR = os.path.join(MODEL_DIR, 'result-{}'.format(mfile))
roundoff_num = 6
TOOL_ID = 'cbmpy'


print(mfile)
print(MODEL_DIR)
print(RESULT_DIR)
model_files = [mfile]

#os.sys.exit()


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
    _ = R.testObjective(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

    T2 = time.time()
    report += 'Test objective: {:.2f}s\n'.format(T2 - T1)

    # Test FVA
    _ = R.testFVA(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

    T3 = time.time()
    report += 'Test FVA: {:.2f}s\n'.format(T3 - T2)

    # Test Gene Deletion
    _ = R.testGeneDeletion(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

    T4 = time.time()
    report += 'Test gene deletions: {:.2f}s\n'.format(T4 - T3)

    # Test Reaction Deletion
    _ = R.testReactionDeletion(testmod, RESULT_DIR, tool_id=TOOL_ID, sigfig=roundoff_num)

    T5 = time.time()
    report += 'Test reaction deletions: {:.2f}s\n'.format(T5 - T4)
    report += 'Total time: {:.2f}s\n'.format(T5 - T0)

report += '\n########################\n'

#format(time.strftime('%Y-%m-%d-%H:%M')

with open(os.path.join(RESULT_DIR, 'curation-timings.txt'), 'w') as F:
    F.write(report)

print(report)


