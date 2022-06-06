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

    for start, stop in zip(starts, stops):
        data[start:stop, :] = 1
        data[int(np.mean([start, stop])),:, :] = peak_value

    return data, stim, starts, stops

class TestFnirslib(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestFnirslib, self).__init__(*args, **kwargs)
        self.data, self.stim, self.starts, self.stops = generate_data(10, 46, 2, 1000, 5)
        self.filename  = 'test_data.nirs'
        self.regions = regions =  [[0, 1, 3, 4],   # APFC
            [2, 5, 6, 7, 8],    #MDPFC
            [14, 15, 16],   #RDPFC
            [10, 11, 12],   #LDPFC
            [9, 18, 19, 21, 22, 28, 31],    #IFC
            [17, 33],   #RBA
            [13, 29],   #LBA
            [20, 23, 24, 25, 26, 30, 32],   #PMC-SMA
            [27, 34, 35, 36, 37, 38],   #M1
            [39, 40, 42, 44],   #V2-V3
            [41, 43, 45] ]  #V1
        scipy.io.savemat(self.filename, {'s':self.stim, 'procResult':{'dc':self.data}})        
        # print(self.data.shape)
        # print(self.stim.shape)

    def test_load_data(self):
        fnirs = Fnirslib(self.filename, self.regions, 0, 'condition_1')
        data, stims = fnirs.load_nirs() # load the data
        self.assertEqual(stims.shape, self.stim.shape)
        self.assertEqual(data.shape, self.data.shape)
        print('test_load_data passed')

    def test_get_ROI_paired(self):
        fnirs = Fnirslib(self.filename, self.regions, 0, 'condition_1')
        data, stims = fnirs.load_nirs() # load the data
        data, stims = fnirs.get_ROI(data, stims, aggMethod='concat')
        self.assertEqual(data.shape, (np.sum(self.stops[:10]-self.starts[:10]), 3, 46))
        print('test_get_ROI_paired passed')

    def test_peak_activation_integration(self):
        fnirs = Fnirslib(self.filename, self.regions, 0, 'condition_1')
        data, stims = fnirs.load_nirs()
        # TODO: test peak activation integration
        print('test_peak_activation_integration passed')

    def test_mean_activation_integration(self):
        fnirs = Fnirslib(self.filename, self.regions, 0, 'condition_1')
        data, stims = fnirs.load_nirs()
        # TODO: test mean activation integration
        print('test_mean_activation_integration passed')

    def test_get_ROI_unpaired(self):
        fnirs = Fnirslib(self.filename, self.regions, 0, 'condition_1', paired=False)
        data, stims = fnirs.load_nirs()
        # TODO: test unpaired
        print('test_get_ROI_unpaired passed')

class TestMetrics(unittest.TestCase):
    """
    Test the metrics
    """
    def __init__(self, *args, **kwargs):
        super(TestMetrics, self).__init__(*args, **kwargs)
        # create a 2d test array
        self.data = np.array([[1,2,3,4,5,6,7,8,9,10,11,12,13],
                            [3,1,2,2,2,2,2,2,2,2,2,2,2],
                            [2,2,2,2,2,2,4,2,2,2,2,2,2],
                            [2,2,2,-2,9,-1,2,2,2,2,2,2,2]]).T

    def test_get_mean_activation(self):
        d = Metrics(self.data)
        self.assertEqual(d.get_mean_activation().shape, (self.data.shape[1],)) # check shape
        self.assertTrue(np.array_equal(d.get_mean_activation(), np.array([np.mean(self.data[:,0]),
                                                                            np.mean(self.data[:,1]),
                                                                            np.mean(self.data[:,2]),
                                                                            np.mean(self.data[:,3])]))) # check values
        print('test_get_mean_activation passed')

    def test_get_peak_activation(self):
        d = Metrics(self.data, peakPadding=1)
        self.assertEqual(d.get_peak_activation().shape, (self.data.shape[1],)) # check shape
        self.assertTrue(np.array_equal(d.get_peak_activation(), np.array([12.5, 2., 8/3., 2.]))) # check values
        print('test_get_peak_activation passed')

    def test_functional_connectivity(self):
        con,_ = Metrics(self.data.T).get_functional_connectivity()
        print(con.shape)
        # get diagonal
        diag = np.diag(np.diag(con))
        print(diag)
        self.assertEqual(con.shape, (self.data.shape[1], self.data.shape[1])) # check shape

if __name__ == '__main__':
    unittest.main()
