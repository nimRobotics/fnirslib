"""
author: @nimrobotics
description: example of how to use the fnirslib package
"""

from fnirslib.fnirslib import Fnirslib
from fnirslib.plots import plotData
import glob
import logging
import datetime
import pandas as pd
import numpy as np
import scipy.io
from pathlib import Path

output_dir = './output_{}'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
# create output directory
Path(output_dir).mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=output_dir+'/logs.log',
                    filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, 
                    encoding='utf-8')

regions =  [[0, 1, 3, 4],   # APFC
            [2, 7, 6, 8, 5],    #MDPFC
            [14, 15, 16],   #RDPFC
            [10, 11, 12],   #LDPFC
            [28, 19, 18, 9, 21, 22, 31],    #IFC
            [17, 33],   #RBA
            [13, 29],   #LBA
            [30, 20, 25, 24, 26, 23, 32],   #PMC-SMA
            [34, 35, 27, 38, 37, 36],   #M1
            [42, 39, 40, 44],   #V2-V3
            [43, 41, 45] ]  #V1
threshold = 0.4
labels = ['APFC', 'MDPFC', 'RDPFC', 'LDPFC', 'IFC', 'RBA', 'LBA', 'PMC-SMA', 'M1', 'V2-V3', 'V1']
in_dir = './rawData'
stimulus=[2,3] # stimulus numbers, 2-normal, 3-attack 
conditions = ['normal', 'attack'] # condition labels
files = glob.glob(in_dir+'/*.nirs') # get all the files in the directory

assert len(files) > 0, 'No files found in the directory'
assert len(stimulus) == len(conditions), 'Number of stimulus should be equal to the len of conditions array'

# initialize a pd df
actDF = pd.DataFrame(columns=['ID', 'sex', 'condition', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37', 'C38', 'C39', 'C40', 'C41', 'C42', 'C43', 'C44', 'C45', 'C46'])
# actDF = pd.DataFrame(columns=['ID', 'sex', 'condition']+labels)

avgCorr = np.zeros((len(regions),len(regions)))
avgZscores = np.zeros((len(regions),len(regions)))
# loop through all the files and conditions
for stim, condition in zip(stimulus, conditions):
    for file in files:
        print("\nProcessing condition '{}' for file {}".format(condition,file))

        try:
            fObj = Fnirslib(file, regions, stim, condition)
            print('Data shape: {}, Stim shape: {}'.format(fObj.data.shape, fObj.stimData.shape))
            fObj.get_ROI()
            fObj.detrend()
            fObj.data = fObj.data[:,0,:] # 0 for HbO, 1 for HbR, 2 for HbT
            peak = fObj.peak_activation(peakPadding=4)
            fObj.mean_activation()

            print('Data shape: {}'.format(fObj.data.shape))
            
            fObj.cluster_channels()
            # fObj.effective_connectivity()
            fObj.data = fObj.data.T #transpose the data, rows are regions, columns are observations
            corr,zscores = fObj.functional_connectivity()
            print('Corr shape: {}, Zscores shape: {}'.format(corr.shape, zscores.shape))
            avgCorr = np.mean( np.array([ avgCorr, corr ]), axis=0 ) # average over files/participants
            avgZscores = np.mean( np.array([ avgZscores, zscores ]), axis=0 ) # average over files/participants

            fObj.save_processed_data(output_dir+'/processed')

            # save the activation data
            actDF.loc[len(actDF)] = [fObj.filepath.split('/')[-1].split('.')[0], fObj.sex, fObj.condition] + list(peak)
        
        except Exception as e:
            print(e)
            logging.error(e)
            continue
    
    # apply threshold
    if threshold is not None:
        avgCorr[np.where(avgZscores < threshold)] = np.NaN
    # save the average correlation for each condition as .mat
    scipy.io.savemat(output_dir+'/{}_avgCorr.mat'.format(condition), mdict={'avgCorr': avgCorr})
    # make plots for functional connectivity
    plot = plotData(avgCorr, labels, output_dir+'/', colormap='jet', dpi=300, title='FC: '+condition, filename='FC_'+condition +'.png') 
    plot.matrixPlot()
    plot.circularPlot()

## TODO: save all data in a CSV file
actDF.to_csv(output_dir+'/activations.csv', index=False)


