"""
author: @nimrobotics
description: example of how to use the fnirslib package
"""

# from fnirslib.fnirslib import Fnirslib
# from fnirslib.plots import plotData
import sys
sys.path.append('../')
from fnirslib.fnirslib import *
from fnirslib.plots import plotData
import glob
import logging
import datetime
import pandas as pd
import numpy as np
import scipy.io
from pathlib import Path
import itertools

# random numpy array
data = np.random.rand(100, 3)
x = plotData(data)
x.line_plot()
