"""
author: @nimrobotics
description: process and prepare data for EC and FC analysis
"""

import numpy as np 
import scipy.io
import scipy.signal

def load_data(file):
    """
    load data from nirs file
    :param file: .nirs file
    :return: data
    """
    nirs = scipy.io.loadmat(file) 
    stimData = np.array(nirs['s'], dtype=np.int64) # stimulus data
    data = np.array(nirs['procResult']['dc'][0][0], dtype=np.float64) # HbO, HbR, HbT values
    return stimData, data

def detrend(data):
    """
    Detrends the data
    :param data: HbO, Hbr or HbT data
    :return: detrended data
    """
    return scipy.signal.detrend(data, axis=0, type='linear')

def makeRegions(data, regions, nRegions=None):
    """
    Returns concatenated data for brain regions
    :param data: HbO, Hbr or HbT data
    :param regions: brain regions
    :param nRegions: number of brain regions
    :return: data for the brain regions
    """
    if nRegions is None:
        nRegions = len(regions)
    assert nRegions == len(regions), 'Number of regions should be equal to the len of regions array'

    outData = np.zeros((data.shape[0], data.shape[1], nRegions))
    for i,region in enumerate(regions):
        outData[:,:,i] = np.mean(data[:,:,region], axis=2) # average over the brain regions
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