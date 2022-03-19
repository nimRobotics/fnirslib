import imp


import numpy as np
import glob
import pandas as pd
from fnirslib.pprocess import load_data
from fnirslib import sanity

in_dir = './rawData'
stim = 2

files = glob.glob(in_dir+'/*.nirs') # get all the files in the directory

for file in files:
    print("\nProcessing file {}".format(file))
    stimData, data = load_data(file) # load data
    print('Data shape: {}, Stim shape: {}'.format(data.shape, stimData.shape))

    nStim, start_stim, end_stim, mean_duration, trial_durations = sanity.stim_check(stimData, stim)
    print("Number of stims: {}".format(nStim))
    print("Mean duration: {}".format(mean_duration))
    df = pd.DataFrame(zip(start_stim, end_stim, trial_durations), columns=['start', 'end', 'duration'])
    print(df)