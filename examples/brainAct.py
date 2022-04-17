"""
author: @nimrobotics
description: calculates the functional connectivity between regions and plots them
"""

from multiprocessing import Condition
import numpy as np
import scipy.io
import glob
import os
import pandas as pd
# from fnirslib.activation import getPeakActivation
# from fnirslib.plots import plotData
import sys
sys.path.append('../fnirslib')
from plots import plotData
from activation import getPeakActivation

if __name__ == '__main__':
    in_dir = "./procDataAct/" #directory of the data
    out_dir = './actData/' #directory to save the plots
    subdirs = [x[0] for x in os.walk(in_dir)][1:] #get all the subdirectories
    threshold=0.4

    females = ['SAI01', 'SAI02', 'SAI04', 'SAI09', 'SAI10', 'SAI14', 'SAI19', 'SAI22', 'SAI25', 'SAI26', 'SAI27', 
                'SAI28', 'SAI29', 'SAI30', 'SAI31', 'SAI32', 'SAI33', 'SAI35', 'SAI36', 'SAI38', 'SAI39', 'SAI40']
    males = ['SAI03', 'SAI05', 'SAI06', 'SAI07', 'SAI08', 'SAI11', 'SAI12', 'SAI13', 'SAI15', 'SAI16', 'SAI17', 
                'SAI18', 'SAI20', 'SAI21', 'SAI23', 'SAI24', 'SAI34', 'SAI37']

    # initialize a pd df
    actDF = pd.DataFrame(columns=['ID', 'sex', 'condition', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C35', 'C36', 'C37', 'C38', 'C39', 'C40', 'C41', 'C42', 'C43', 'C44', 'C45', 'C46'])

    for dir in subdirs:
        condition = dir.split('/')[-1]
        files = glob.glob(dir+'/*.mat') # get all the files in the directory
        # avgActivation = np.zeros(np.
        for file in files:
            print('Processing file: ', file)
            ID = file.split('/')[-1].split('.')[0][1:]
            if 'SAI'+ID in females:
                sex = 'F'
            if 'SAI'+ID in males:
                sex = 'M'

            print('\nProcessing file: {}, condition: {}'.format(ID, condition))
            data = scipy.io.loadmat(file) #load data from the directory
            data = data['pdata'] #get the data from the dictionary
            data = getPeakActivation(data, interval=4)
            actDF.loc[len(actDF)] = [ID, sex, condition] + list(data)

    # save df to csv
    actDF.to_csv(out_dir+'actDF.csv', index=False)