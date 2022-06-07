"""
author: @nimrobotics
description: class for processing fnirs data
"""

import numpy as np
import pandas as pd
import scipy.io
import scipy.signal
from . import metrics
import logging
from pathlib import Path

class Fnirslib:
    def __init__(self, filepath, regions, stimNumber, condition, sex='NA', paired=True):
        """
        Initialize the class
        :param filepath: .nirs or .snirf filepath
        :param regions: brain regions, type: list of lists
        :param stimNumber: stimulus number/condition, type: int
        :param condition: condition, type: str
        :param sex: sex of the participant, M or F, type: str
        :param paired: True if each trial has start and end stim, type: bool
        """
        self.filepath = filepath
        self.regions = regions
        self.stimNumber = stimNumber
        self.condition = condition
        self.sex = sex
        self.paired = paired
        self.nRegions = len(regions) # number of brain regions
        self.nChannels = sum([len(e) for e in regions]) # number of channels
        logging.info("Processing file '{}', with condition '{}' ...".format(self.filepath,self.condition))        
        logging.info("Number of channels: {}, Number of regions: {}".format(self.nChannels, self.nRegions))

    def load_nirs(self):
        """
        Load nirs data from filepath
        :return: data, stims
        """
        nirs = scipy.io.loadmat(self.filepath) 
        stims = np.array(nirs['s'], dtype=np.int64) # stimulus data
        data = np.array(nirs['procResult']['dc'][0][0], dtype=np.float64) # HbO, HbR, HbT values
        logging.info("Successfully loaded data from {}".format(self.filepath))
        logging.info("Data shape: {}, Stimulus data shape: {}".format(data.shape, stims.shape))
        return data, stims

    def load_snirf(self):
        """
        Loads snirf file
        :return: data, stims
        """
        raise NotImplementedError
        stims = None
        data = None
        logging.info("Successfully loaded data from {}".format(self.filepath))
        logging.info("Data shape: {}, Stimulus data shape: {}".format(data.shape, stims.shape))
        return data, stims

    def sanity_check(self, data, stims, trialTimes):
        """
        :param stims: stimulus data
        :param data: data
        :return: None
        """
        assert stims.shape[1]>=self.stimNumber+1, 'Stimulus column {} not found'.format(self.stimNumber)
        assert stims.shape[0] == data.shape[0], "Number of observations in stimData and data do not match"
        assert data.shape[1] == 3, "Number of channels in data is not 3 (HbO, HbR, HbT)"
        assert data.shape[2] == self.nChannels, "Number of channels in data does not match number of channels in regions"
        assert np.count_nonzero(stims[:,self.stimNumber])!= 0, 'No stims found'
        assert not isinstance(stims, np.int64), 'Stimulus data should be int64'
        logging.info("Number of stims: {}".format(np.count_nonzero(stims[:,self.stimNumber])))

        if self.paired:
            assert np.count_nonzero(stims[:,self.stimNumber])%2==0, "Number of stims should be even" # if stims have start and stop
            loc = np.where(stims[:,self.stimNumber]==1)[0]
            start_stim = loc[::2] # get start indices
            end_stim = loc[1::2] # get end indices
            trial_durations = end_stim - start_stim
            mean_duration = np.mean(trial_durations)
            logging.info("Trial starts: {}".format(start_stim))
            logging.info("Trial ends: {}".format(end_stim))
        elif not self.paired:
            mean_duration = np.mean(trialTimes)
            logging.info("Trial starts: {}".format(np.where(stims[:,self.stimNumber]==1)[0]))
            logging.info("Trial durations: {}".format(trialTimes))
        logging.info("Mean trial duration: {}".format(mean_duration))

    def _find_islands(self, x):
        """
        Finds islands of 1s in the data
        :param x: data
        :return: number of islands
        """
        return np.sum(x[1:] & ~x[:-1]) + x[0]

    def _insert_end_stim(self, stims):
        '''
        insert end stims to the trials
        :param stims: stimulus data
        :return: stims with end stims
        '''
        startIdx = np.nonzero(stims[:,self.stimNumber])[0]  # get index of start stim
        stopIdx = startIdx + np.array(self.trialTimes*self.freq, dtype=np.int64)[:startIdx.shape[0]]

        # if last idx is greater than the length of the data, set it equal to length of data
        if stopIdx[-1]>stims.shape[0]:
            stopIdx[-1] = stims.shape[0]-1

        # construct new stimData, removing extra trials
        stims[:,self.stimNumber] = 0 # set all stims to 0
        stims[startIdx,self.stimNumber] = 1 # set start stims to 1
        stims[stopIdx,self.stimNumber] = 1 # set end stims to 1
        return stims

    def _equalize_trial_length(self, stims):
        '''
        make number of observations equal across trials, by setting them equal
        to min number of observations
        '''
        loc = np.where(stims[:,self.stimNumber]==1)[0]
        start = loc[::2] # get start indices
        end = loc[1::2] # get end indices
        stims[:,self.stimNumber] = 0 # set all stims to 0
        stims[start,self.stimNumber] = 1 # set start stims to 1
        stims[start+np.min(end-start),self.stimNumber] = 1 # set end stims to 1
        return stims

    def get_ROI(self, data, stims,  equalize=False,  aggMethod='concat', trialTimes=None, freq=None):
        """
        get ROI data for the stimulus condition
        :param data: data, type: numpy array
        :param stims: stimulus data, type: numpy array
        :param equalize: equalize the number of obs in all trials, automatically set True if aggMethod is 'mean', type: bool
        :param aggMethod: method to aggregate data, either 'concat' or 'mean' the trials, type: str
        :param trialTimes: array of trial durations, cannot be None if stimPair is False, type: list
        :param freq: frequency of the data, type: float
        :return: ROI data, concatenated data for all trials with given stimulus/condition
        """
        if not self.paired:
            # print('# stims before pairing: ', np.count_nonzero(stims[:,self.stimNumber]))
            stims = self._insert_end_stim(stims)
            # print('# stims after pairing: ', np.count_nonzero(stims[:,self.stimNumber]))

        assert np.count_nonzero(stims[:,self.stimNumber])%2==0, "Number of stims should be even"

        if equalize or aggMethod.lower()=='mean':
            stims = self._equalize_trial_length(stims)

        # create a mask for the stimulus
        mask = np.cumsum(stims[:,self.stimNumber]) % 2   # set values to 1 between two consecutive 1s
        islands = self._find_islands(mask) # number of islands
        # print('# of islands: ', islands)
        if aggMethod.lower()=='concat':
            data = data[mask==1]  # apply the mask to the data
        if aggMethod.lower()=='mean':
            idx = np.where(mask!=0)[0]
            data = np.array(np.split(data[idx],np.where(np.diff(idx)!=1)[0]+1))
            data = np.mean(data, axis=0) # mean over the trials
            # print('data shape after mean', data.shape)
        logging.info('Number of observations in ROI: {}'.format(data.shape[0]))
        return data, stims

    def cluster_channels(self, data):
        """
        Merge channels into regions using mean
        :param data: data
        :return: clustered data for the brain regions
        """
        if data.ndim==2:
            outData = np.zeros((data.shape[0], self.nRegions))
            for i,region in enumerate(self.regions):
                outData[:,i] = np.mean(data[:,region], axis=1)
        elif data.ndim==3:
            outData = np.zeros((data.shape[0], data.shape[1], self.nRegions))
            for i,region in enumerate(self.regions):
                outData[:,:,i] = np.mean(data[:,:,region], axis=2)
        data = outData
        return data

    def detrend(self, data):
        """
        Detrends the data
        :param data: data
        :return: detrended data
        """
        return scipy.signal.detrend(data, axis=0, type='linear')

    def normalize(self, data):
        """
        Normalizes the data
        :param data: data
        :return: normalized data
        """
        return data/np.max(data)

    def peak_activation(self, data, peakPadding=4):
        """
        Finds the peak activation of the data
        :param data: data
        :param peakPadding: number of samples to pad the peak
        :return: peak activations
        """
        return metrics.Metrics(data, peakPadding).get_peak_activation()

    def mean_activation(self, data):
        """
        Finds the mean activation of the data
        :param data: data
        :return: mean activations 
        """
        return metrics.Metrics(data).get_mean_activation()

    def functional_connectivity(self, data):
        """
        Finds functional connectivity
        :param data: data
        :return: correlation matrix, z-scores
        """
        return metrics.Metrics(data).get_functional_connectivity()

    def effective_connectivity(self, data):
        """
        Finds effective connectivity
        :param data: data
        :return:  None
        """
        return metrics.Metrics(data).get_effective_connectivity()

    def save_processed_data(self, data, stims, dir):
        """
        Saves processed data to .mat files
        :param data: data
        :param stims: stimulus data
        :param dir: directory to save the data
        :return: None
        """
        Path(dir+'/'+self.condition).mkdir(parents=True, exist_ok=True) # create a directory for the condition
        fname = dir+'/'+self.condition+'/'+self.filepath.split('/')[-1].split('.')[0]+'.mat'
        scipy.io.savemat(fname, {"pdata": data, "nTrials": np.count_nonzero(stims[:,self.stimNumber])/2})
        logging.info('Saved data to {}'.format(fname))