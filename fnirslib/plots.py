"""
author: @nimrobotics
description: methods for creating fnirs plots
"""

import numpy as np
from mne_connectivity.viz import plot_connectivity_circle
import matplotlib.pyplot as plt

class plotData(object):
    """
    Plots the correlation matrix
    """
    def __init__(self, data, labels=None, savedir='./', colormap='viridis', dpi=None, title=None, filename=None):
        """
        Plots the correlation matrix
        :param data: correlation matrix
        :param labels: labels for the regions
        :param savedir: directory to save the plots
        :param colormap: colormap for the plot
        :param dpi: dpi for the plot
        :param title: title of the plot
        :param filename: filename of the plot
        :return: None
        """
        self.data = data
        self.labels = labels
        self.savedir = savedir
        self.title = title
        self.filename = filename
        self.colormap = colormap
        self.dpi = dpi

    def line_plot(self):
        """
        Plot brain data line plot
        each row is a different line
        :return: None
        """
        plt.figure()
        plt.plot(self.data)   
        # add row numbers as legend
        plt.legend(range(self.data.shape[0]))         
        plt.savefig(self.savedir +'line_', dpi=self.dpi)
        



    def circularPlot(self):
        """
        Plots the correlation circular plot
        :return: None
        """
        fig = plt.figure(num=None, figsize=(8, 8), facecolor='white')
        plot_connectivity_circle(self.data, self.labels, textcolor='black', colormap=self.colormap, 
                                facecolor='white', vmax=1, vmin=0, linewidth=2.5, node_colors=['gray', 'silver'],                                
                                title=self.title, fig=fig, show=False) 
        plt.savefig(self.savedir +'circle_'+self.filename, dpi=self.dpi)
        plt.cla() # clear the figure
        fig.clf() # clear the figure
        plt.close() # close the figure

    def matrixPlot(self):
        """
        Plots the correlation matrix
        :return: None
        """
        plt.imshow(self.data, cmap=self.colormap)
        plt.title(self.title)
        plt.xticks(np.arange(0, len(self.labels)), self.labels, rotation=90)
        plt.yticks(np.arange(0, len(self.labels)), self.labels)
        plt.colorbar()
        # set min and max values
        plt.clim(0, 1)
        plt.savefig(self.savedir +'matrix_'+self.filename, dpi=self.dpi)
        plt.clf() # clear the figure
        plt.close() # close the figure
        plt.cla() # clear the figure

    def connectome(self):
        """
        Plots brain connectome
        :return: None
        """
        raise NotImplementedError

    def connectome_directed(self):
        """
        Plots directed brain connectome
        :return: None
        """
        raise NotImplementedError

    def topograph(self):
        """
        Plot brain topographic maps
        :return: None
        """
        raise NotImplementedError
