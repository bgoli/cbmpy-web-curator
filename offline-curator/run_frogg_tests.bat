@echo off

echo RUNNNING FROGG TEST MODELS SMALLEST TO LARGEST

::python offline_curator.py ..\test-models\frogg\VvuMBEL943_2022.xml
python offline_curator.py ..\test-models\frogg\iDS372.xml
::python offline_curator.py ..\test-models\frogg\Gmetallireducens_ac_Fe+Updated.xml
::python offline_curator.py ..\test-models\frogg\Canto-Encalada2022-FBA+of+simultaneous+degradation+of+ammonia+and+pollutants.xml
::python offline_curator.py ..\test-models\frogg\iJN1463.xml
::python offline_curator.py ..\test-models\frogg\iDK1463.xml
::python offline_curator.py ..\test-models\frogg\Human-GEM.xml

dir ..\test-models\frogg
