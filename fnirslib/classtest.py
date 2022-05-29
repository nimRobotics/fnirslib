from fnirslib import Fnirslib
import glob
import logging
import datetime

# 'logs_{}.log'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
logging.basicConfig(filename='logs.log',
                    filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, 
                    encoding='utf-8')

regions =  [[0, 1, 3, 4],
            [2, 7, 6, 8, 5],
            [14, 15, 16],
            [10, 11, 12],
            [28, 19, 18, 9, 21, 22, 31],
            [17, 31],
            [13, 29],
            [30, 20, 25, 24, 26, 23, 32],
            [34, 35, 27, 38, 37, 36],
            [42, 39, 40, 44],
            [43, 41, 45]]

in_dir = './rawData'
stimulus=[2,3] # stimulus numbers, 2-normal, 3-attack 
conditions = ['normal', 'attack'] # condition labels
files = glob.glob(in_dir+'/*.nirs') # get all the files in the directory

assert len(files) > 0, 'No files found in the directory'
assert len(stimulus) == len(conditions), 'Number of stimulus should be equal to the len of conditions array'

# loop through all the files and conditions
for stim, condition in zip(stimulus, conditions):
    for file in files:
        print("\nProcessing condition '{}' for file {}".format(condition,file))

        try:
            fObj = Fnirslib(file, regions, stim, condition)
            print('Data shape: {}, Stim shape: {}'.format(fObj.data.shape, fObj.stimData.shape))
            fObj.getROI()
            fObj.makeRegions()
            fObj.detrend()
            fObj.data = fObj.data[:,0,:] # 0 for HbO, 1 for HbR, 2 for HbT
            fObj.peakActivation(peakPadding=4)
            fObj.meanActivation()
            fObj.functionalConnectivity()
            fObj.effectiveConnectivity()

        # except all errors
        except Exception as e:
            print(e)
            logging.error(e)
            continue

        # Path(out_dir+'/'+condition).mkdir(parents=True, exist_ok=True) # create a directory for the condition
        # fname = out_dir+'/'+condition+'/'+file.split('/')[-1].split('.')[0]+'.mat'
        # scipy.io.savemat(fname, {"pdata": data, "nTrials": np.count_nonzero(stimData[:,stim])/2})
        # print('Finished processing file, saved as: '+fname)

        


