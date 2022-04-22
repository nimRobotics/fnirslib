import numpy as np

def getMeanActivation(data):
    """
    Get mean activation for each region
    :return: mean activation for each region
    """
    return np.mean(data, axis=0)

def getPeakActivation(data, interval):
    """
    Get peak activation for each region
    :param data: HbO, Hbr or HbT data
    :param interval: interval to be considered surrounding the peak
    :return: peak activation for each region
    """
    # initialize array
    peakActivation = np.zeros(data.shape[1])
    # iterate over each column of data
    for i in range(data.shape[1]):
        maxIdx = np.argmax(data[:,i])
        maxInterval = data[maxIdx-interval:maxIdx+interval,i]
        peakActivation[i] = np.mean(maxInterval)

    return peakActivation