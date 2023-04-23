@echo off

echo RUNNNING FROGG TEST MODELS SMALLEST TO LARGEST

python offline_curator.py ..\FROGG-hackathon\input-sbml\VvuMBEL943_2022.xml
::python offline_curator.py ..\FROGG-hackathon\input-sbml\iDS372.xml
::python offline_curator.py ..\FROGG-hackathon\input-sbml\Gmetallireducens_ac_Fe+Updated.xml
::python offline_curator.py ..\FROGG-hackathon\input-sbml\Canto-Encalada2022-FBA+of+simultaneous+degradation+of+ammonia+and+pollutants.xml
::python offline_curator.py ..\FROGG-hackathon\input-sbml\iJN1463.xml
::python offline_curator.py ..\FROGG-hackathon\input-sbml\iDK1463.xml
::python offline_curator.py ..\FROGG-hackathon\input-sbml\Human-GEM.xml

dir ..\FROGG-hackathon\input-sbml
