import numpy as np
import pandas as pd
import scipy.io
import scipy.signal
from metrics import Metrics
import logging

class Fnirslib:
    def __init__(self, filepath, regions, stimNumber, condition, sex='NA', equalize=False, paired=True, aggMethod='concat', trialTimes=None, freq=None):
        """
        Initialize the class
        :param filepath: .nirs file, type: str
        :param regions: brain regions, type: list of lists
        :param stimNumber: stimulus number/condition, type: int
        :param condition: condition, type: str
        :param sex: sex of the participant, M or F, type: str
        :param equalize: equalize the number of obs in all trials, automatically set True if aggMethod is 'average', type: bool
        :param paired: True if each trial has start and end stim, type: bool
        :param aggMethod: method to aggregate data, either 'concat' or 'average' the trials, type: str
        :param trialTimes: array of trial times, cannot be None if stimPair is False, type: list
        :param freq: frequency of the data, type: float
        """
        self.filepath = filepath
        self.regions = regions
        self.stimNumber = stimNumber
        self.condition = condition
        self.sex = sex
        self.equalize = equalize
        self.paired = paired
        self.aggMethod = aggMethod
        self.trialTimes = trialTimes
        self.freq = freq
        self.nRegions = len(regions) # number of brain regions
        self.nChannels = sum([len(e) for e in regions]) # number of channels
        self.data = None # fnirs data (nobs, hbo/hbr/hbt, nchannels)
        self.stimData = None # stimulus data
        if filepath.endswith('.nirs'):
            self._load_nirs()
        elif filepath.endswith('.snirf'):
            self._load_snirf()
        self._sanity_check()

    def _load_nirs(self):
        """
        Load nirs data from filepath
        :param filepath: .nirs filepath
        :return: data, stimData
        """
        logging.warning("Log from calss nirs data from {}".format(self.filepath))
        # assert 1==0, "Not implemented"
        nirs = scipy.io.loadmat(self.filepath) 
        self.stimData = np.array(nirs['s'], dtype=np.int64) # stimulus data
        self.data = np.array(nirs['procResult']['dc'][0][0], dtype=np.float64) # HbO, HbR, HbT values

    def _load_snirf(self):
        """
        Loads snirf file
        :return: data, stimData
        """
        raise NotImplementedError
        self.stimData = None
        self.data = None

    def _sanity_check(self):
        """
        check if stimData has stimNumber
        :param stimData: stimulus data
        :param stimNumber: stimulus number
        :return: stimData stats
        """
        print("Number of stims: {}".format(np.count_nonzero(self.stimData[:,self.stimNumber])))

        assert self.stimData.shape[0] == self.data.shape[0], "Number of observations in stimData and data do not match"
        assert self.data.shape[1] == 3, "Number of channels in data is not 3 (HbO, HbR, HbT)"
        assert self.data.shape[2] == self.nChannels, "Number of channels in data does not match number of channels in regions"


        if self.paired:
            assert np.count_nonzero(self.stimData[:,self.stimNumber])%2==0, "Number of stims should be even" # if stims have start and stop
            loc = np.where(self.stimData[:,self.stimNumber]==1)[0]
            start_stim = loc[::2] # get start indices
            end_stim = loc[1::2] # get end indices
            trial_durations = end_stim - start_stim
            mean_duration = np.mean(trial_durations)
            print("Mean duration: {}".format(mean_duration))
        else:
            print("Mean duration: {}".format(np.mean(self.trialTimes)))

        assert self.stimData.shape[1]>=self.stimNumber+1, 'Stimulus column {} not found'.format(self.stimNumber)
        assert np.count_nonzero(self.stimData[:,self.stimNumber])!= 0, 'No stims found'
        assert not isinstance(self.stimData, np.int64), 'Stimulus data should be int64'

    def _find_islands(self, x):
        """
        Finds islands of 1s in the data
        :param x: data
        :return: number of islands
        """
        return np.sum(x[1:] & ~x[:-1]) + x[0]

    def _insertEndStim(self):
        '''
        insert end stims to the trials
        '''
        startIdx = np.nonzero(self.stimData[:,self.stimNumber])[0]  # get index of start stim
        stopIdx = startIdx + np.array(self.trialTimes*self.freq, dtype=np.int64)[:startIdx.shape[0]]

        # if last idx is greater than the length of the data, set it equal to length of data
        if stopIdx[-1]>self.stimData.shape[0]:
            stopIdx[-1] = self.stimData.shape[0]-1

        # construct new stimData, removing extra trials
        self.stimData[:,self.stimNumber] = 0 # set all stims to 0
        self.stimData[startIdx,self.stimNumber] = 1 # set start stims to 1
        self.stimData[stopIdx,self.stimNumber] = 1 # set end stims to 1

    def _equalizeTrialLength(self):
        '''
        make number of observations equal across trials, by setting them equal
        to min number of observations
        '''
        loc = np.where(self.stimData[:,self.stimNumber]==1)[0]
        start = loc[::2] # get start indices
        end = loc[1::2] # get end indices
        self.stimData[:,self.stimNumber] = 0 # set all stims to 0
        self.stimData[start,self.stimNumber] = 1 # set start stims to 1
        self.stimData[start+np.min(end-start),self.stimNumber] = 1 # set end stims to 1

    def getROI(self):
        """
        get ROI data for the stimulus condition
        :return: concatenated data for all trials with given stimulus/condition
        """
        if not self.paired:
            print('# stims before pairing: ', np.count_nonzero(self.stimData[:,self.stimNumber]))
            self._insertEndStim()
            print('# stims after pairing: ', np.count_nonzero(self.stimData[:,self.stimNumber]))

        assert np.count_nonzero(self.stimData[:,self.stimNumber])%2==0, "Number of stims should be even"

        if self.equalize or self.aggMethod.lower()=='average':
            self._equalizeTrialLength()

        # create a mask for the stimulus
        mask = np.cumsum(self.stimData[:,self.stimNumber]) % 2   # set values to 1 between two consecutive 1s
        islands = self._find_islands(mask) # number of islands
        print('# of islands: ', islands)
        if self.aggMethod.lower()=='concat':
            self.data = self.data[mask==1]  # apply the mask to the data
        if self.aggMethod.lower()=='average':
            idx = np.where(mask!=0)[0]
            self.data = np.array(np.split(self.data[idx],np.where(np.diff(idx)!=1)[0]+1))
            print('data shape', self.data.shape)
            self.data = np.mean(self.data, axis=0) # average over the trials
            print('data shape after average', self.data.shape)
        print('nobs in ROI',self.data.shape)

    def makeRegions(self):
        """
        Merge channels into regions using mean
        :return: data for the brain regions
        """
        outData = np.zeros((self.data.shape[0], self.data.shape[1], self.nRegions))
        for i,region in enumerate(self.regions):
            outData[:,:,i] = np.mean(self.data[:,:,region], axis=2)
        self.data = outData

    def detrend(self):
        """
        Detrends the data
        """
        self.data = scipy.signal.detrend(self.data, axis=0, type='linear')

    def normalize(self):
        """
        Normalizes the data
        """
        self.data = self.data/np.max(self.data)

    def peakActivation(self, peakPadding=4, verbose=False):
        """
        Finds the peak activation of the data
        :param peakPadding: number of samples to pad the peak
        :param verbose: print peak activation
        :return: peak activations
        """
        return Metrics(self.data, peakPadding, verbose=verbose).getPeakActivation()

    def meanActivation(self, verbose=False):
        """
        Finds the mean activation of the data
        :param verbose: print mean activation
        :return: mean activations 
        """
        return Metrics(self.data, verbose=verbose).getMeanActivation()

    def functionalConnectivity(self, verbose=False):
        """
        Finds functional connectivity
        :param verbose: print functional connectivity
        :return: correlation matrix, z-scores
        """
        return Metrics(self.data, verbose=verbose).getFunctionalConnectivity()

    def effectiveConnectivity(self, verbose=False):
        """
        Finds effective connectivity
        :param verbose: print effective connectivity
        :return:  None
        """
        return Metrics(self.data, verbose=verbose).getEffectiveConnectivity()