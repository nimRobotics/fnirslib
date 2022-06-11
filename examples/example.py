"""
author: @nimrobotics
description: example of how to use the fnirslib package
"""

# from fnirslib.fnirslib import Fnirslib
# from fnirslib.plots import plotData
import sys
sys.path.append('../')
from fnirslib.fnirslib import *
from fnirslib.plots import plotData
import glob
import logging
import datetime
import pandas as pd
import numpy as np
import scipy.io
from pathlib import Path
import itertools

output_dir = './output_{}'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
# create output directory
Path(output_dir).mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=output_dir+'/logs.log',
                    filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, 
                    encoding='utf-8')

regions =  [[0, 1, 3, 4],   # APFC
            [2, 5, 6, 7, 8],    #MDPFC
            [14, 15, 16],   #RDPFC
            [10, 11, 12],   #LDPFC
            [9, 18, 19, 21, 22, 28, 31],    #IFC
            [17, 33],   #RBA
            [13, 29],   #LBA
            [20, 23, 24, 25, 26, 30, 32],   #PMC-SMA
            [27, 34, 35, 36, 37, 38],   #M1
            [39, 40, 42, 44],   #V2-V3
            [41, 43, 45] ]  #V1
threshold = 0.4
labels = ['APFC', 'MDPFC', 'RDPFC', 'LDPFC', 'IFC', 'RBA', 'LBA', 'PMC-SMA', 'M1', 'V2-V3', 'V1']
in_dir = './rawData'
stimulus=[2,3] # stimulus numbers, 2-normal, 3-attack 
conditions = ['normal', 'attack'] # condition labels
files = glob.glob(in_dir+'/*.nirs') # get all the files in the directory

assert len(files) > 0, 'No files found in the directory'
assert len(stimulus) == len(conditions), 'Number of stimulus should be equal to the len of conditions array'

actDF = pd.DataFrame(columns=['ID', 'sex', 'condition']+['C'+str(i) for i in range(sum([len(e) for e in regions]))]) # store data for each channel
actClusteredDF = pd.DataFrame(columns=['ID', 'sex', 'condition']+labels) # store data for each brain region
FCDF = pd.DataFrame(columns=['ID', 'sex', 'condition']+[i+'-'+j for i,j in list(itertools.combinations(labels, 2))]) # store FC con data

# loop through all the files and conditions
for stimNumber, condition in zip(stimulus, conditions):
    avgCorr = np.zeros((len(regions),len(regions)))
    avgZscores = np.zeros((len(regions),len(regions)))
    for file in files:
        print("\nProcessing condition '{}' for file {}".format(condition,file))
        try:
            # perform activation analysis on mean aggregated data
            fnirs = Fnirslib(file, regions, stimNumber, condition) # initialize the fnirs object
            logging.info("Activation analysis! averaging trial data")
            data, stims = fnirs.load_nirs() # load the data
            fnirs.sanity_check(data, stims) # check the data
            data, stims = fnirs.get_ROI(data, stims, aggMethod='mean')
            # data = fnirs.detrend(data) # detrend the data
            # data = fnirs.cluster_channels(data) # cluster the channels into regions
            data = data[:,0,:] # 0 for HbO, 1 for HbR, 2 for HbT
            peak = fnirs.peak_activation(data, peakPadding=5) # get the peak activation
            mean = fnirs.mean_activation(data) # get the mean activation
            actDF.loc[len(actDF)] = [file.split('/')[-1].split('.')[0], fnirs.sex, fnirs.condition] + list(peak)
            print(peak.shape)
            fnirs.save_processed_data(data, stims, output_dir+'/processed_act')

            # perform connectivity analysis on concatenated data
            fnirs = Fnirslib(file, regions, stimNumber, condition) # initialize the fnirs object
            logging.info("Connectivity analysis! concatenating trial data")
            data, stims = fnirs.load_nirs() # load the data
            fnirs.sanity_check(data, stims) # check the data
            data, stims = fnirs.get_ROI(data, stims, aggMethod='concat', equalize=False) # get the ROI data
            data = fnirs.detrend(data) # detrend the data
            data = fnirs.cluster_channels(data) # cluster the channels into regions
            data = data[:,0,:] # 0 for HbO, 1 for HbR, 2 for HbT
            # econ = fnirs.effective_connectivity(data)
            corr,zscores = fnirs.functional_connectivity(data.T)
            print('Corr shape: {}, Zscores shape: {}'.format(corr.shape, zscores.shape))
            avgCorr = np.mean( np.array([ avgCorr, corr ]), axis=0 ) # average over files/participants
            avgZscores = np.mean( np.array([ avgZscores, zscores ]), axis=0 ) # average over files/participants
            fnirs.save_processed_data(data, stims, output_dir+'/processed_con')
            # save the data for each individual, each file thresholded separately
            if threshold is not None:
                corr[np.where(np.abs(zscores) < threshold)] = 0
            triuCorr = corr[np.triu_indices(len(corr), 1)] # get the upper triangle of the correlation matrix
            FCDF.loc[len(FCDF)] = [file.split('/')[-1].split('.')[0], fnirs.sex, fnirs.condition] + list(triuCorr)
        except Exception as e:
            print(e)
            logging.error(e)
            continue
    
    # save average correlation, zscores as .mat and .csv
    scipy.io.savemat(output_dir+'/{}_avgCorr.mat'.format(condition), mdict={'avgCorr': avgCorr})
    scipy.io.savemat(output_dir+'/{}_avgZscores.mat'.format(condition), mdict={'avgZscores': avgZscores})
    pd.DataFrame(avgCorr, index=labels, columns=labels).to_csv(output_dir+'/{}_avgCorr.csv'.format(condition))
    pd.DataFrame(avgZscores, index=labels, columns=labels).to_csv(output_dir+'/{}_avgZscores.csv'.format(condition))
    # apply threshold to the average data
    if threshold is not None:
        avgCorr[np.where(avgZscores < threshold)] = np.NaN
    # save the average correlation matrix after thresholding
    scipy.io.savemat(output_dir+'/{}_avgCorrThresholded.mat'.format(condition), mdict={'avgCorr': avgCorr})
    pd.DataFrame(avgCorr, index=labels, columns=labels).to_csv(output_dir+'/{}_avgCorrThresholded.csv'.format(condition))
    
    # make plots for functional connectivity
    plot = plotData(avgCorr, labels, output_dir+'/', colormap='jet', dpi=300, title='FC: '+condition, filename='FC_'+condition +'.png') 
    plot.matrixPlot()
    plot.circularPlot()

## TODO: save all data in a CSV file
actDF.to_csv(output_dir+'/activations.csv', index=False)
FCDF.to_csv(output_dir+'/FC.csv', index=False)


