"""
author: @nimrobotics
description: 
    - extract data for particular stimulus and get concatenated ROI
    - average over brain regions
    - extract HBO
    - linear detrend data 
    - equalize trial length

CAUTION: unlike MATLAB 0-based is used by default
"""

import numpy as np 
import scipy.io
import scipy.signal
import glob
from pathlib import Path
from fnirslib.pprocess import getROI, makeRegions, detrend, load_data
# import sys
# sys.path.append('../fnirslib')
# from pprocess import getROI, makeRegions, detrend, load_data

if __name__  == '__main__':
    # define brain regions, each row is a brain region with elements as channel numbers
    regions =  [    [0, 1, 3, 4],
                    [2, 7, 6, 8, 5],
                    [14, 15, 16],
                    [10, 11, 12],
                    [28, 19, 18, 9, 21, 22, 31],
                    [17, 31],
                    [13, 29],
                    [30, 20, 25, 24, 26, 23, 32],
                    [34, 35, 27, 38, 37, 36],
                    [42, 39, 40, 44],
                    [43, 41, 45] ]

    nRegions = len(regions) # number of brain regions
    nChannels = sum([len(e) for e in regions]) # number of probes
    in_dir = './rawData'
    out_dir = './procDataAct'
    stimulus=[2,3] # stimulus numbers, 2-normal, 3-attack 
    conditions = ['normal', 'attack'] # condition labels
    files = glob.glob(in_dir+'/*.nirs') # get all the files in the directory

    print("Starting data processing............................")
    print("Input directory: {} \nOutput directory: {}".format(in_dir, out_dir))
    print("Number of brain regions: {} \nnumber of channels: {}".format(nRegions, nChannels))
    print("Processing stimulus: {}".format(conditions))
    print("Number of files: ", len(files))

    assert len(files) > 0, 'No files found in the directory'
    assert len(stimulus) == len(conditions), 'Number of stimulus should be equal to the len of conditions array'

    # loop through all the files and conditions
    for stim, condition in zip(stimulus, conditions):
        for file in files:
            print("\nProcessing condition '{}' for file {}".format(condition,file))
            stimData, data = load_data(file) # load data
            print('Data shape: {}, Stim shape: {}'.format(data.shape, stimData.shape))

            assert np.count_nonzero(stimData[:,stim])%2==0, "Number of stims should be even" # if stims have start and stop
            assert stimData.shape[1]>=stim+1, 'Stimulus column {} not found'.format(stim)
            assert np.count_nonzero(stimData[:,stim])<= 20, 'Number of stims should be less than 20'
            assert np.count_nonzero(stimData[:,stim])!= 0, 'No stims found'

            print('Identified stims: ', np.count_nonzero(stimData[:,stim]))
            data = getROI(data,stimData,stim, equalize=True, stimPair=True, aggMethod='average') # extract the trials
            # data = getROI(data,stimData,stim,equalize=True,stimPair=False,trialTimes=trialTimes, freq=freq) # extract the trials
            if data is None:
                continue

            data = makeRegions(data, regions) # get data for brain regions
            data = detrend(data) # detrend the data
            data = data[:,0,:] # 0 for HbO, 1 for HbR, 2 for HbT
            Path(out_dir+'/'+condition).mkdir(parents=True, exist_ok=True) # create a directory for the condition
            fname = out_dir+'/'+condition+'/'+file.split('/')[-1].split('.')[0]+'.mat'
            scipy.io.savemat(fname, {"pdata": data, "nTrials": np.count_nonzero(stimData[:,stim])/2})
            print('Finished processing file, saved as: '+fname)