"""
author: @nimrobotics
description: calculates the effective connectivity between regions and plots them
"""

import numpy as np
import scipy.io
import glob
import sys
sys.path.append('../utils')
from plots import plotData

dir = "./process3/" #directory of the data
outdir = 'process3/' #directory to save the plots
regions = 3 #number of regions
files = glob.glob(dir+'/*_.mat') # get all the files in the directory
for file in files:
    print('Processing condition: ', file)
    data = scipy.io.loadmat(file) #load data from the directory
    fval = data['fval'] #fval
    pval = data['pval'] #pval
    sig = data['sig'] #sig
    cd = data['cd'] #cd
    print('fval shape: ',fval.shape)
    print('\nfval \n',fval)
    print('pval shape: ',pval.shape)
    print('sig shape: ',sig.shape)
    print('\nsig \n',sig)
    print(cd.shape)

    # elementwise multiplication of fval and sig(0/1)
    fval_sig = np.multiply(fval, sig)
    print(fval_sig.shape)
    print('\nfval_sig \n',fval_sig)

    # fval_sig = np.mean(fval_sig, axis=2) # average over files
    # print(fval_sig.shape)
    # fval = np.mean(fval, axis=2)

    labels = ['PFC', 'PM-MC', 'VC'] #labels for the regions
    condition = file.split('/')[-1].split('.')[0] #get the condition name
    plot = plotData(fval_sig, labels, outdir, colormap='viridis', dpi=300, title='EC: '+condition, filename='EC_'+condition +'.png') 
    plot.matrixPlot()
    plot.circularPlot()
