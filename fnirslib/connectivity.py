import numpy as np

def functionalConnectivity(data):
    '''
    Calculates the functional connectivity between regions
    :param data: 2D array (each row represents a variable, and each column a single observation of all those variables)
    :return: correlation matrix
    '''
    corr = np.corrcoef(data)  # correlation matrix
    zscores = np.arctanh(corr) #convert to tanh space
    #set diagonal elements to NaN
    for i in range(corr.shape[0]):
        corr[i, i] = np.NaN 
    return corr, zscores

def effectiveConnectivity(data):
    '''
    USE MATLAB MVGC toolbox to calculate the effective connectivity
    Calculates the effective connectivity between regions
    :param data: 2D array (each row represents a variable, and each column a single observation of all those variables)
    :return: correlation matrix
    '''
    raise NotImplementedError