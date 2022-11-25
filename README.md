# CBMPyWeb 
A web-based curation tool for genome scale, constraint-based models developed by bgoli (https://github.com/bgoli). Links to the active servers, documentation, a wiki, downloadable packages and more are now available on the CBMPyWeb OSF.io project pages.

https://osf.io/t6mh3/

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


## Curatable test models
- frogg: FROGG analysis development models
- general: random selection of models


## FROGG-hackathon
Models and reference results implemented as part of the FROGG-hackathon.


(C) Brett G. Olivier, Amsterdam, 2021 - 2022.
