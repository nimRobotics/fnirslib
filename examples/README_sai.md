# SAI_ecfc
EC - FC analysis for SAI data

# Processing steps
1. `rawData` contains raw fNRIS files after initial processing with MatLab Homer2
2. `python3 process.py`: takes input from `rawData`, stores condition wise output in `procData` subdirs
3. Functional connectivity: use `python3 FC.py`, uses data from `procData` and stores output plots in `fcPlots`
4. Effective connectivity: 
    * process using the `ec.m` file, `ec.m` needs `mvgc` toolbox (run `setup.m` in mvgc dir to install). `ec.m` takes input from `procData` and saves EC data files for each condition
    * `python3 EC.py` make plots from data generated via the `ec.m`