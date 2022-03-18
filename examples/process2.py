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
# import sys
# sys.path.append('../utils')
# from process_utils import getROI, makeRegions, detrend
def detrend(data):
    """
    Detrends the data
    :param data: HbO, Hbr or HbT data
    :return: detrended data
    """
    return scipy.signal.detrend(data, axis=0, type='linear')

def makeRegions(data, regions):
    """
    Returns concatenated data for brain regions
    :param data: HbO, Hbr or HbT data
    :param regions: brain regions
    :return: data for the brain regions
    """
    # outData = np.zeros((data.shape[0], data.shape[1], regions.shape[0]))
    # for i,region in enumerate(regions):
    #     region = np.array(region)
    #     print('region: ', region)
    #     # print(region-1)
    #     region = region[region!=0]-1 # remove zeros and convert to 0-based indexing
    #     print('number of regios',region)
    #     outData[:,:,i] = np.mean(data[:,:,region], axis=2) # average over the brain regions

    outData = np.zeros((data.shape[0], data.shape[1], regions.shape[0]))
    for i,region in enumerate(regions):
        region = np.array(region)
        region = region[region!=0]-1 # remove zeros and convert to 0-based indexing
        outData[:,:,i] = np.mean(data[:,:,region], axis=2) # average over the brain regions
        print('number of regios',region)
    return outData

def find_islands(x):
    """
    Finds islands of 1s in the data
    :param x: data
    :return: number of islands
    """
    return np.sum(x[1:] & ~x[:-1]) + x[0] 

def equalizeTrialLength(stimData, stimNumber):
    '''
    make number of observations equal across trials, by setting them equal
    to min number of observations
    stimData: stimulus data with both start and end stims
    stimNumber: stimulus number/condition
    return: stimData with equal number of observations
    '''
    loc = np.where(stimData[:,stimNumber]==1)[0]
    even = loc[::2] # get start indices
    odd = loc[1::2] # get end indices
    stimData[:,stimNumber] = 0 # set all stims to 0
    stimData[even,stimNumber] = 1 # set start stims to 1
    stimData[even+np.min(odd-even),stimNumber] = 1 # set end stims to 1
    return stimData

def insertEndStim(stimData, stimNumber, trialTimes, freq):
    '''
    insert end stims for each stim
    stimData: stimulus data with just start stims
    stimNumber: stimulus number/condition
    trialTimes: array of trial times
    freq: sampling frequency
    return: stimData with both start and end stims
    '''
    # if data has only start stim, make a pair by adding end stim
    startIdx = np.nonzero(stimData[:,stimNumber])[0]  # get index of start stim
    stopIdx = startIdx + np.array(trialTimes*freq, dtype=np.int64)[:startIdx.shape[0]]
    print(trialTimes)
    print(np.array(trialTimes*freq, dtype=np.int64)[:startIdx.shape[0]])
    print(startIdx)
    print(stopIdx)

    # if last idx is greater than the length of the data, set it equal to length of data
    if stopIdx[-1]>stimData.shape[0]:
        stopIdx[-1] = stimData.shape[0]-1
    print(stopIdx)

    # construct new stimData, removing extra trials
    stimData[:,stimNumber] = 0 # set all stims to 0
    stimData[startIdx,stimNumber] = 1 # set start stims to 1
    stimData[stopIdx,stimNumber] = 1 # set end stims to 1
    return stimData

def getROI(data, stimData, stimNumber, equalize, stimPair, trialTimes=None, freq=None ):
    """
    get ROI data for the stimulus condition
    :param data: HbO, Hbr or HbT data
    :param stimData: stimulus
    :param stimNumber: stimulus number
    :param equalize: equalize the number of observation for every trial
    :param stimPair: True if each stim already has start and end, False if only start stim
    :param trialTimes: array of trial times, cannot be None if stimPair is False
    :param freq: sampling frequency, cannot be None if stimPair is False
    :return: concatenated data for all trials with given stimulus/condition
    """
    if stimPair==False:
        print('# stims before pairing: ', np.count_nonzero(stimData[:,stimNumber]))
        stimData = insertEndStim(stimData, stimNumber, trialTimes, freq)
        print('# stims after pairing: ', np.count_nonzero(stimData[:,stimNumber]))
    if np.count_nonzero(stimData[:,stimNumber])%2 != 0:
        print("#################### Warning: ####################")
        print('Number of stims should be even.')
        return None
    if equalize:
        stimData = equalizeTrialLength(stimData, stimNumber)

    # create a mask for the stimulus
    mask = np.cumsum(stimData[:,stimNumber]) % 2   # set values to 1 between two consecutive 1s
    # islands = find_islands(mask) # number of islands
    data = data[mask==1]  # apply the mask to the data
    print('nobs in ROI',data.shape)
    return data

if __name__  == '__main__':
    # define brain regions, each row is a brain region with elements as probe numbers
    # regions =  np.array([   [1, 2, 4, 5, 0, 0, 0],
    #                         [3, 8, 7, 9, 6, 0, 0],
    #                         [15, 16, 17, 0, 0, 0, 0],
    #                         [11, 12, 13, 0, 0, 0, 0],
    #                         [29, 20, 19, 10, 22, 23, 32],
    #                         [18, 32, 0, 0, 0, 0, 0],
    #                         [14, 30, 0, 0, 0, 0, 0],
    #                         [31, 21, 26, 25, 27, 24, 33],
    #                         [35, 36, 28, 39, 38, 37, 0],
    #                         [43, 40, 41, 45, 0, 0, 0],
    #                         [44, 42, 46, 0, 0, 0, 0]])

    regions =  np.array([   [1, 2, 4, 5, 3, 8, 7, 9, 6, 15, 16, 17,
                            11, 12, 13, 29, 20, 19, 10, 22, 23, 32],

                            [18, 32, 0, 0, 0, 0, 0,
                            14, 30, 0, 0, 0, 0, 0,
                            31, 21, 26, 25, 27, 24, 33,
                            35, 36, 28, 39, 38, 37, 0],
                            
                            [43, 40, 41, 45, 0, 0, 0,
                            44, 42, 46, 0, 0, 0, 0]])

    nRegions = regions.shape[0] # number of brain regions
    print("nRegions:",nRegions)
    nProbes = np.sum(regions!=0) # number of probes

    print("Preparing data for FC/EC............................")
    dir_path = './rawData'
    # dir_path = './testdata'
    out_dir = './process2'
    stimulus=[2,3] # stimulus numbers, 0/1-practice, 2-normal, 3-attack
    conditions = ['normal', 'attack'] # condition labels
    files = glob.glob(dir_path+'/*.nirs') # get all the files in the directory

    for stim,condition in zip(stimulus, conditions):
        pData=[]
        pNtrials=[]
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

            if data is None:
                continue
            data = makeRegions(data, regions) # get data for brain regions
            data = detrend(data) # detrend the data
            data = data[:,0,:] # 0 for HbO, 1 for HbR, 2 for HbT
            print(data)

            # below code wont work if equalize is not set to True
            print('data shape',data.shape)
            print('data shape',data.shape[0])
            print('nobs', data.shape[0]/(np.count_nonzero(stimData[:,stim])/2))
            # pData.append(data)
            pData.append(np.array_split(data, int(np.count_nonzero(stimData[:,stim])/2)))


        print('\n')
        print(len(pData[0]))
        print('pData shape', np.array(pData[0]).shape)

        t1=[[],[],[],[],[]] # bins for five trials
        for data in pData:
            for i,trial in enumerate(data):
                print('\n',trial.shape)
                # trial = np.vstack((trial, np.zeros((tShape-trial.shape[0],nRegions))))
                print(trial.shape)
                t1[i].append(trial)

        print(len(t1)) # number of trials
        print(len(t1[0])) # number of files
        print(len(t1[1])) # number of files
        print(len(t1[2])) # number of files
        print(len(t1[3])) # number of files
        print(len(t1[4])) # number of files

        for j,trial in enumerate(t1):
            print('\n')
            shape = [x.shape[0] for x in trial]
            minLenght = min(shape)
            for i,file in enumerate(trial):
                trial[i]=file[:minLenght,:]
                print(trial[i].shape)
            t1[j] = np.mean(trial, axis=0)
            print(t1[j].shape)    
            # print(t1[j])
            print('\n')

        outArr =  np.vstack(t1)
        print(outArr.shape)

        fname = out_dir+'/'+condition+'.mat'
        scipy.io.savemat(fname, {"pdata": outArr})
