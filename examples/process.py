"""
author: @nimrobotics
description: prepare the data for EC and FC analysis

desined for SAI data
"""

import numpy as np 
import scipy.io
import scipy.signal
import glob
from pathlib import Path
import sys
sys.path.append('../utils')
from process_utils import getROI, makeRegions, detrend

if __name__  == '__main__':
    # define brain regions, each row is a brain region with elements as probe numbers
    regions =  np.array([   [1, 2, 4, 5, 0, 0, 0],
                            [3, 8, 7, 9, 6, 0, 0],
                            [15, 16, 17, 0, 0, 0, 0],
                            [11, 12, 13, 0, 0, 0, 0],
                            [29, 20, 19, 10, 22, 23, 32],
                            [18, 32, 0, 0, 0, 0, 0],
                            [14, 30, 0, 0, 0, 0, 0],
                            [31, 21, 26, 25, 27, 24, 33],
                            [35, 36, 28, 39, 38, 37, 0],
                            [43, 40, 41, 45, 0, 0, 0],
                            [44, 42, 46, 0, 0, 0, 0]])

    nRegions = regions.shape[0] # number of brain regions
    nProbes = np.sum(regions!=0) # number of probes

    print("Preparing data for FC/EC............................")
    dir_path = './rawData'
    out_dir = './procData'
    stimulus=[2,3] # stimulus numbers, 0/1-practice, 2-normal, 3-attack
    conditions = ['normal', 'attack'] # condition labels
    files = glob.glob(dir_path+'/*.nirs') # get all the files in the directory

    for stim,condition in zip(stimulus, conditions):
        for file in files:
            print('\nProcessing condition {} for file {}'.format(condition,file))

            nirs = scipy.io.loadmat(file) # load the data
            stimData = np.array(nirs['s'], dtype=np.int64) # stimulus corrected manually
            data = np.array(nirs['procResult']['dc'][0][0], dtype=np.float64) # HbO, Hbr, HbT values
            print('data shape',data.shape)
            print('stims shape',stimData.shape)

            # check if stim column is present
            if stimData.shape[1]<stim+1:
                print("#################### Warning: ####################")
                print("Missing stims column, skipping file:", file)
                continue

            # skip file if no stims are found
            if np.count_nonzero(stimData[:,stim])==0:
                print("#################### Warning: ####################")
                print("Stim {} not found in file: {}".format(condition, file))
                continue

            if np.count_nonzero(stimData[:,stim])%2 != 0:
                print("#################### Warning: ####################")
                print('stimulus numbers are not even, skipping file:')
                continue
            
            # taking only first 20 stims if more than 20
            if np.count_nonzero(stimData[:,stim]) > 20:
                print("#################### Warning: ####################")
                print("Too many stims #{}, taking first 20".format(np.count_nonzero(stimData[:,stim])))
                stimIdxes = np.nonzero(stimData[:,stim])[0]  # get index of stims
                stimData[:,stim] = 0  # set all stims to 0
                stimData[stimIdxes[0:20],stim] = 1  # set first 10 stims to 1

            # TODO: this block is specific to SAI and should be removed
            # processing only attack first 5 and reliable last 5 trials
            try:
                stimIdxes = np.nonzero(stimData[:,stim])[0]  # get index of stims
                stimData[:,stim] = 0  # set all stims to 0
                if condition == 'normal':
                    stimData[stimIdxes[10:],stim] = 1
                elif condition == 'attack':
                    stimData[stimIdxes[:10],stim] = 1
            except:
                continue
            if np.count_nonzero(stimData[:,stim])==0:
                print("Stim {} not found in file: {}".format(condition, file))
                continue

            print('Identified stims: ', np.count_nonzero(stimData[:,stim]))
            data = getROI(data,stimData,stim,equalize=True, stimPair=True) # extract the trials
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