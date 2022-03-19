"""
author: @nimrobotics
description: calculates the effective connectivity between regions and plots them
"""

import numpy as np
import scipy.io
import glob
from fnirslib.connectivity import effectiveConnectivity
from fnirslib.plots import plotData

dir = "./ecMatlab/" #directory of the data
outdir = 'ecPlots/' #directory to save the plots
regions = 11 #number of regions
files = glob.glob(dir+'/*.mat') # get all the files in the directory
for file in files:
    print('Processing condition: ', file)
    data = scipy.io.loadmat(file) #load data from the directory
    fval = data['fval_all'] #fval
    pval = data['pval_all'] #pval
    sig = data['sig_all'] #sig
    cd = data['cd_all'] #cd
    print(fval.shape)
    print(pval.shape)
    print(sig.shape)
    print(cd.shape)

    # elementwise multiplication of fval and sig(0/1)
    fval_sig = np.multiply(fval, sig)
    print(fval_sig.shape)

    fval_sig = np.mean(fval_sig, axis=2) # average over files
    print(fval_sig.shape)
    fval = np.mean(fval, axis=2)

    labels = ['APFC', 'MDPFC', 'LDPFC', 'RDPFC', 'IFC', 'PMC-SMA', 'LBA', 'RBA', 'M1', 'V2-V3', 'V1'] #labels for the regions
    condition = file.split('/')[-1].split('.')[0] #get the condition name
    plot = plotData(fval_sig, labels, outdir, colormap='viridis', dpi=300, title='EC: '+condition, filename='EC_'+condition +'.png') 
    plot.matrixPlot()
    plot.circularPlot()
