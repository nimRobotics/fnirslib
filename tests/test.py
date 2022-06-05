from readline import read_init_file
from tracemalloc import start
import unittest
import sys
import scipy.io
sys.path.append('../')
from fnirslib.fnirslib import *
from fnirslib.metrics import *

output_dir = './test_output'
Path(output_dir).mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=output_dir+'/logs.log',
                    filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, 
                    encoding='utf-8')

def generate_data(num_trials, num_channels, num_conditions=2, num_samples=1000, peak_value=2):
    """
    Generate data for testing
    :param num_trials: number of trials per condition
    :param num_channels: number of channels
    :param num_conditions: number of conditions
    :param num_samples: number of samples
    :param peak_value: peak value
    :return: data
    """
    np.random.seed(5)

    data = np.zeros((num_samples, 3, num_channels))
    stim = np.zeros((num_samples, num_conditions))
    starts = np.linspace(0, num_samples-100, num_trials*num_conditions).astype(int) + np.random.randint(0,20,num_trials*num_conditions)
    stops = np.sort(starts + 10 + np.random.randint(0,20,num_trials*num_conditions)) # end of each trial
    # print('core stim values')
    # print(starts[:10])
    # print(stops[:10])

    for i in range(num_conditions):
        stim[starts[i*10:i*10+10], i] = 1
        stim[stops[i*10:i*10+10], i] = 1

    i=0
    for start, stop in zip(starts, stops):
        data[start:stop, :] = 1
        data[int(np.mean([start, stop])),:, :] = peak_value
        print('### i:', i)
        i=i+1
        print(data[start:stop,0,0])


    return data, stim, starts, stops

class TestFnirslib(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestFnirslib, self).__init__(*args, **kwargs)
        self.data, self.stim, self.starts, self.stops = generate_data(10, 46, 2, 1000, 5)
        self.filename  = 'test_data.nirs'
        self.regions = regions =  [[0, 1, 3, 4],   # APFC
            [2, 7, 6, 8, 5],    #MDPFC
            [14, 15, 16],   #RDPFC
            [10, 11, 12],   #LDPFC
            [28, 19, 18, 9, 21, 22, 31],    #IFC
            [17, 33],   #RBA
            [13, 29],   #LBA
            [30, 20, 25, 24, 26, 23, 32],   #PMC-SMA
            [34, 35, 27, 38, 37, 36],   #M1
            [42, 39, 40, 44],   #V2-V3
            [43, 41, 45] ]  #V1
        scipy.io.savemat(self.filename, {'s':self.stim, 'procResult':{'dc':self.data}})        
        # print(self.data.shape)
        # print(self.stim.shape)

    def test_load_data(self):
        fnirs = Fnirslib(self.filename, self.regions, 0, 'condition_1')
        self.assertEqual(fnirs.stimData.shape, self.stim.shape)
        self.assertEqual(fnirs.data.shape, self.data.shape)
        print('test_load_data passed')

    def test_get_ROI_paired(self):
        fnirs = Fnirslib(self.filename, self.regions, 0, 'condition_1', aggMethod='average', equalize=True)
        fnirs.get_ROI()
        print("data",fnirs.data[:,0,0])
        self.assertEqual(fnirs.data.shape, (np.sum(self.stops[:10]-self.starts[:10]), 3, 46))
        # fnirs.detrend()
        fnirs.data = fnirs.data[:,0,:] # 0 for HbO, 1 for HbR, 2 for HbT
        print(fnirs.data.shape)
        print(fnirs.data[0])
        peak = fnirs.peak_activation(peakPadding=0)
        self.assertEqual(peak.shape, (46,))
        print(peak)

        print('test_get_ROI_paired passed')


    # def test_get_ROI_unpaired(self):
    #     NotImplementedError




    # def test_peak_activation(self):
    #     peak_activation = 
    #     print(peak_activation)
    #     self.assertEqual(True, True)


# class TestMetrics(unittest.TestCase):
#     def __init__(self, *args, **kwargs):
#         super(TestMetrics, self).__init__(*args, **kwargs)
#         self.data, self.stim = generate_data(10, 44, 2, 1000, 2)
#         print(self.data.shape)
#         print(self.stim.shape)

#     def test_get_mean_activation(self):
#         d = Metrics(self.data)
#         self.assertEqual(d.get_mean_activation().shape, (3,44))
#         self.assertEqual(d.get_mean_activation()[0,0], 1)

#     def test_get_peak_activation(self):
#         data = np.ones((10,3,3))*2
#         # data[]
#         d = Metrics(data)
#         self.assertEqual(d.get_peak_activation().shape, (3,3))    
#         self.assertEqual(d.get_peak_activation()[0,0], 2)

if __name__ == '__main__':
    unittest.main()
