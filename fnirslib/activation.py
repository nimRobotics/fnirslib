import numpy as np

def getMeanActivation():
    """
    Get mean activation for each region
    :return: mean activation for each region
    """
    raise NotImplementedError

def getPeakActivation(data):
    """
    Get peak activation for each region
    :return: peak activation for each region
    """
    # raise NotImplementedError
    # find index of max value
    maxIdx = np.argmax(data, axis=0)
    # get max value
    maxVal = data[maxIdx]
    print('maxVal: ',maxVal)
    print('maxIdx: ',maxIdx)
    print('maxVal.shape: ',maxVal.shape)
    
    return np.max(data, axis=0)