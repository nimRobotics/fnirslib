import numpy as np

def stim_check(stimData, stimNumber):
    """
    check if stimData has stimNumber
    :param stimData: stimulus data
    :param stimNumber: stimulus number
    :return: stimData stats
    """

    # number of stims
    nStim = np.sum(stimData[:,stimNumber])
    assert nStim%2==0, "Number of stims is not even"

    loc = np.where(stimData[:,stimNumber]==1)[0]
    start_stim = loc[::2] # get start indices
    end_stim = loc[1::2] # get end indices

    trial_durations = end_stim - start_stim
    mean_duration = np.mean(trial_durations)
    print("Mean duration: {}".format(mean_duration))
    return nStim, start_stim, end_stim, mean_duration, trial_durations