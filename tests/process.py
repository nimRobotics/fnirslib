"""
author: @nimrobotics
description: 
    - generate test data
"""

import numpy as np 
import scipy.io
import scipy.signal


if __name__  == '__main__':
    # read fnirs data
    nirs = scipy.io.loadmat('032.nirs')
    stimData = np.array(nirs['s'], dtype=np.int64) # stimulus data
    data = np.array(nirs['procResult']['dc'][0][0], dtype=np.float64) # HbO, HbR, HbT values
    print(data.shape)
    print(stimData.shape)
    baselineStart, baselineEnd = np.where(stimData[:,0] == 1)[0][0], np.where(stimData[:,0] == 1)[0][-1]
    print(baselineStart, baselineEnd)
    data[baselineStart:baselineEnd,:] = 2
    # make all data zero
    data[:] = 0
    # get index of non-zero stims
    stimIndex = np.where(stimData[:,2] != 0)[0]
    print(stimIndex)
    #get even indices
    start = stimIndex[::2]
    print(start)
    # get odd indices
    stop = stimIndex[1::2]
    print(stop)

    # set values between all start and end stims to 1
    for i in range(len(start)):
        data[start[i]-20:start[i],:] = 2
        data[start[i]:stop[i],:,:] = 1
        # mean idx of start and end stims
        meanIdx = (start[i]+stop[i])//2
        # set mean idx to 4
        # data[meanIdx,:,:] = 4
        data[start[i]+13,:,:] = 4

    print(data[5370:5687,0,0])
    # save data
    scipy.io.savemat('032_test.nirs', {'s':stimData, 'procResult':{'dc':[data]}})
    
    
 


