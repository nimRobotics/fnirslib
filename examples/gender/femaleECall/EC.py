"""
author: @nimrobotics
description: calculates the effective connectivity between regions and plots them
"""

from asyncore import write
import numpy as np
import scipy.io
import glob
import csv

phase = 'attack' #normal or attack
files = glob.glob(phase+'/*.mat') # get all the files in the directory
for file in files:
    print('Processing condition: ', file)
    data = scipy.io.loadmat(file) #load data from the directory
    fval = data['fval'] #fval
    pval = data['pval'] #pval
    sig = data['sig'] #sig
    cd = data['cd'] #cd
    print(fval.shape)
    print(pval.shape)
    print(sig.shape)
    print(cd.shape)

    print('\n fval \n',fval)
    print('\n flatten fval \n',fval.flatten())

    # write the array to a csv file
    with open(phase+'EC.csv', 'a') as f:
        # write the array into rows
        writer = csv.writer(f)
        name = file.split('/')[1].split('.')[0]
        writer.writerow([name]+list(fval.flatten()))
