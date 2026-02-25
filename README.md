download birdnet extract the file and 
do 'pip install birdnet'

This is a project that uses BirdNet to analyse birdactivity in Estenstadsmarka


py -3.12 -m birdnet_analyzer.analyze .\sounds\realsound --output result --lat 63.2332 --lon 10.2730 --week 6 --min_conf 0.5 --skip_existing_results
