# cbmpy-web-curator
A web-based curation tool for genome scale, constraint-based models

## offline-curator

This is an offline version of the FROGG curator that only requires a Python 3 (tested with 3.8) environment with CBMPy installed (https://systemsbioinformatics.github.io/cbmpy/).

### Usage
To run the analysis on a single model call with model file:
```bash
python offline_curator.py <model-file>.xml
```

If a directory is given as an input then all files with .xml will be analysed.
```bash
python offline_curator.py <model-directory>
```

Results of the analysis will be output in the model input directory.


## Curation test models
- frogg: FROGG analysis development models
- general: random selection of models


## FROGG-hackathon
Models and reference results implemented as part of the FROGG-hackathon.



