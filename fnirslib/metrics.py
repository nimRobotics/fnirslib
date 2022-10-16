"""
author: @nimrobotics
description: metrics for fnirs data
"""

import numpy as np
import logging

class Metrics:
    """
    Get features from fnirs data, features are:
    1. mean activation
    2. peak activation
    3. functional connectivity
    4. effective connectivity
    """
    def __init__(self, data, peakPadding=None):
        """
        :param data: HbO/Hbr/HbT data for ROI
        :param peakPadding: padding to be considered surrounding the peak
        """
        self.data = data
        self.peakPadding = peakPadding

    def get_mean_activation(self):
        """
        Get mean activation for each region
        :return: mean activation for each region
        """
        return np.mean(self.data, axis=0)

    def _peak_activation(self, data, baseline=None):
        """
        Get peak activation for each region
        :param baseline: baseline to be subtracted from the data
        :return: peak activation for each region
        """
        peakActivation = np.zeros(data.shape[1])
        # iterate over each column of data i.e. each channel
        for i in range(data.shape[1]):
            maxIdx = np.argmax(data[:,i])
            # check if padding overshoots the data at start or end
            if maxIdx-self.peakPadding < 0:
                logging.warning('Peak activation padding overshoots data at start')
                peakActivation[i] = np.mean(data[0:maxIdx+self.peakPadding+1,i])
            elif maxIdx+self.peakPadding+1 > data.shape[0]:
                logging.warning('Peak activation padding overshoots data at end')
                peakActivation[i] = np.mean(data[maxIdx-self.peakPadding:data.shape[0],i])
            else:
                # print(data[maxIdx-self.peakPadding:maxIdx+self.peakPadding+1,i])
                peakActivation[i] = np.mean(data[maxIdx-self.peakPadding:maxIdx+self.peakPadding+1,i])
            # subtract baseline if baseline is provided
            if baseline is not None:
                peakActivation[i] -= baseline[i]
        return peakActivation

    def get_peak_activation(self, baseline=None):
        """
        Get peak activation for each region
        :param data: HbO, Hbr or HbT data
        :param baseline: baseline to be subtracted from data
        :param padding: padding to be considered surrounding the peak
        :return: peak activation for each region
        """
        if self.data.ndim == 2:
            return self._peak_activation(self.data, baseline)
        if self.data.ndim == 1:
            act_data = []
            for trial in range(self.data.shape[0]):
                print('trial',trial)
                print('data',self.data[trial].shape)
                print('baseline',baseline[trial].shape)
                print('data',self.data[trial][:,0,:].shape)
                act_data.append(self._peak_activation(self.data[trial][:,0,:], baseline[trial]))
            act_data = np.array(act_data)
            return np.mean(act_data, axis=0)


    def get_functional_connectivity(self):
        """
        Get functional connectivity between regions
        :return: correlation matrix, z-scores
        """
        corr = np.corrcoef(self.data)  # correlation matrix
        zscores = np.arctanh(corr) #convert to tanh space
        #set diagonal elements to NaN
        for i in range(corr.shape[0]):
            corr[i, i] = np.NaN 
        return corr, zscores

    def get_effective_connectivity(self):
        """
        TIP: Use MATLAB MVGC toolbox to calculate the effective connectivity
        Get effective connectivity between regions
        :return: correlation matrix
        """
        assert False, 'Not implemented: effective connectivity'