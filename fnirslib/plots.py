"""
author: @nimrobotics
description: methods for creating brain connectivity plots
"""

import numpy as np
import mne
import matplotlib.pyplot as plt

class plotData(object):
    """
    Plots the correlation matrix
    """
    def __init__(self, data, labels, savedir, colormap='viridis', dpi=None, title=None, filename=None):
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

    def circularPlot(self):
        """
        Plots the correlation circular plot
        :return: None
        """
        fig = plt.figure(num=None, figsize=(8, 8), facecolor='white')
        mne.viz.plot_connectivity_circle(self.data, self.labels, textcolor='black', colormap='jet', 
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
        plt.imshow(self.data, cmap='viridis')
        plt.title(self.title)
        plt.xticks(np.arange(0, len(self.labels)), self.labels, rotation=90)
        plt.yticks(np.arange(0, len(self.labels)), self.labels)
        plt.colorbar()
        plt.savefig(self.savedir +'matrix_'+self.filename, dpi=self.dpi)
        plt.clf() # clear the figure
        plt.close() # close the figure
        plt.cla() # clear the figure

    def brainPlot(self):
        """
        Plots the correlation matrix as a brain map
        :return: None
        """
        raise NotImplementedError
