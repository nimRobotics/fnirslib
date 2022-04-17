"""
author: @nimrobotics
description: calculates the functional connectivity between regions and plots them
"""

import numpy as np
import scipy.io
import glob
import os
# from fnirslib.connectivity import functionalConnectivity
# from fnirslib.plots import plotData
import sys
sys.path.append('../fnirslib')
from connectivity import functionalConnectivity
from plots import plotData
from activation import getPeakActivation

if __name__ == '__main__':
    in_dir = "./procDataAct/" #directory of the data
    out_dir = './actData/' #directory to save the plots
    subdirs = [x[0] for x in os.walk(in_dir)][1:] #get all the subdirectories
    labels = ['APFC', 'MDPFC', 'LDPFC', 'RDPFC', 'IFC', 'PMC-SMA', 'LBA', 'RBA', 'M1', 'V2-V3', 'V1'] #labels for the regions
    threshold=0.4
    for dir in subdirs:
        files = glob.glob(dir+'/*.mat') # get all the files in the directory
        # avgActivation = np.zeros(np.
        for file in files:
            print('Processing file: {}, condition: {}'.format(file, dir.split('/')[-1]))
            data = scipy.io.loadmat(file) #load data from the directory
            data = data['pdata'] #get the data from the dictionary
            print(data.shape)
            data = getPeakActivation(data)
            print(data)
            print(data.shape)

        # # save .mat file
        # condition = dir.split('/')[-1] #get the condition name
        # save_name = out_dir + 'FC_'+condition + '.mat'
        # scipy.io.savemat(save_name, {'corr': avgCorr})

        # # make plots
        # plot = plotData(avgCorr, labels, out_dir, colormap='viridis', dpi=300, title='FC: '+condition, filename='FC_'+condition +'.png') 
        # plot.matrixPlot()
        # plot.circularPlot()
