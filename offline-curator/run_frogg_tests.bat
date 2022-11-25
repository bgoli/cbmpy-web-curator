@echo off

:: set MODEL_DIR=d:\Development\cbmpy-web-curator\test-models\frogg 
:: conda activate flaskdev

echo RUNNNING FROGG TEST MODELS SMALLEST TO LARGEST

python offline_curator.py d:\Development\cbmpy-web-curator\test-models\frogg\VvuMBEL943_2022.xml
python offline_curator.py d:\Development\cbmpy-web-curator\test-models\frogg\iDS372.xml
python offline_curator.py d:\Development\cbmpy-web-curator\test-models\frogg\Gmetallireducens_ac_Fe+Updated.xml
python offline_curator.py d:\Development\cbmpy-web-curator\test-models\frogg\Canto-Encalada2022-FBA+of+simultaneous+degradation+of+ammonia+and+pollutants.xml
python offline_curator.py d:\Development\cbmpy-web-curator\test-models\frogg\iJN1463.xml
python offline_curator.py d:\Development\cbmpy-web-curator\test-models\frogg\iDK1463.xml
python offline_curator.py d:\Development\cbmpy-web-curator\test-models\frogg\Human-GEM.xml

dir d:\Development\cbmpy-web-curator\test-models\frogg
