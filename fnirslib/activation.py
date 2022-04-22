import numpy as np

def getMeanActivation(data):
    """
    Get mean activation for each region
    :return: mean activation for each region
    """
    return np.mean(data, axis=0)

def getPeakActivation(data, padding):
    """
    Get peak activation for each region
    :param data: HbO, Hbr or HbT data
    :param padding: padding to be considered surrounding the peak
    :return: peak activation for each region
    """
    # initialize array
    peakActivation = np.zeros(data.shape[1])
    # iterate over each column of data
    for i in range(data.shape[1]):
        maxIdx = np.argmax(data[:,i])
        # check if padding overshoots the data at start or end
        if maxIdx-padding < 0:
            print('padding overshoots the data at start')
            peakActivation[i] = np.mean(data[0:maxIdx+padding,i])
        elif maxIdx+padding > data.shape[0]:
            print('padding overshoots the data at end')
            peakActivation[i] = np.mean(data[maxIdx-padding:data.shape[0],i])
        else:
            print('padding within the data')
            peakActivation[i] = np.mean(data[maxIdx-padding:maxIdx+padding,i])

    return peakActivation