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

    def getMeanActivation(self):
        """
        Get mean activation for each region
        :return: mean activation for each region
        """
        return np.mean(self.data, axis=0)

    def getPeakActivation(self):
        """
        Get peak activation for each region
        :param data: HbO, Hbr or HbT data
        :param padding: padding to be considered surrounding the peak
        :return: peak activation for each region
        """
        # initialize array
        peakActivation = np.zeros(self.data.shape[1])
        # iterate over each column of data
        for i in range(self.data.shape[1]):
            maxIdx = np.argmax(self.data[:,i])
            # check if padding overshoots the data at start or end
            if maxIdx-self.peakPadding < 0:
                logging.warning('Peak activation padding overshoots data at start')
                peakActivation[i] = np.mean(self.data[0:maxIdx+self.peakPadding,i])
            elif maxIdx+self.peakPadding > self.data.shape[0]:
                logging.warning('Peak activation padding overshoots data at end')
                peakActivation[i] = np.mean(self.data[maxIdx-self.peakPadding:self.data.shape[0],i])
            else:
                peakActivation[i] = np.mean(self.data[maxIdx-self.peakPadding:maxIdx+self.peakPadding,i])
        return peakActivation

    def getFunctionalConnectivity(self):
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

    def getEffectiveConnectivity(self):
        """
        TIP: Use MATLAB MVGC toolbox to calculate the effective connectivity
        Get effective connectivity between regions
        :return: correlation matrix
        """
        assert False, 'Not implemented: effective connectivity'