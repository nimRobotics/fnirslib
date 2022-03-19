"""
author: @nimrobotics
description: calculates the functional connectivity between regions and plots them
"""

import numpy as np
import scipy.io
import glob
import os
from fnirslib.connectivity import functionalConnectivity
from fnirslib.plots import plotData

if __name__ == '__main__':
    in_dir = "./procData/" #directory of the data
    out_dir = './fcData/' #directory to save the plots
    subdirs = [x[0] for x in os.walk(in_dir)][1:] #get all the subdirectories
    labels = ['APFC', 'MDPFC', 'LDPFC', 'RDPFC', 'IFC', 'PMC-SMA', 'LBA', 'RBA', 'M1', 'V2-V3', 'V1'] #labels for the regions
    regions = 11 #number of regions
    threshold=0.4
    for dir in subdirs:
        files = glob.glob(dir+'/*.mat') # get all the files in the directory
        avgCorr = np.zeros((regions,regions))
        avgZscores = np.zeros((regions,regions))
        for file in files:
            print('Processing file: ', file)
            data = scipy.io.loadmat(file) #load data from the directory
            data = data['pdata'] #get the data from the dictionary
            data = data.T #transpose the data, rows are regions, columns are observations
            corr,zscores = functionalConnectivity(data) #calculate the correlation matrix
            avgCorr = np.mean( np.array([ avgCorr, corr ]), axis=0 ) # average over files/participants
            avgZscores = np.mean( np.array([ avgZscores, zscores ]), axis=0 ) # average over files/participants
        # apply threshold
        if threshold is not None:
            avgCorr[np.where(avgZscores < threshold)] = np.NaN

        # save .mat file
        condition = dir.split('/')[-1] #get the condition name
        save_name = out_dir + 'FC_'+condition + '.mat'
        scipy.io.savemat(save_name, {'corr': avgCorr})

        # make plots
        plot = plotData(avgCorr, labels, out_dir, colormap='viridis', dpi=300, title='FC: '+condition, filename='FC_'+condition +'.png') 
        plot.matrixPlot()
        plot.circularPlot()
