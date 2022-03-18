from nilearn import plotting
import matplotlib.pyplot as plt
import numpy as np
import scipy.io
import matplotlib.patches as patches

def pltEffCon(inarr, instring, idx):

  XL = np.tril(inarr) #lower triangular matrix
  XL = XL + XL.T - np.diag(np.diag(XL))

  XU = np.triu(inarr) #upper triangular matrix
  XU = XU + XU.T - np.diag(np.diag(XU))

  print('\n',inarr)
  print('\n',XL)
  print('\n',XU)

  # XU =np.zeros(XL.shape)
  plotting.plot_connectome(XU, coordinates, display_mode ='z',
                          annotate = False, edge_cmap = 'viridis', alpha = 0.01,
                              node_color ='k',node_kwargs = {"alpha":0.35},edge_kwargs = {"linewidth":5}, axes = axs[idx], edge_threshold='20%', colorbar = True)
  # plotting.plot_connectome(XL, coordinates2, display_mode ='z', 
  #                         annotate = False, edge_cmap = 'viridis', alpha = 0.01,
  #                             node_color ='k',node_kwargs = {"alpha":0.35}, edge_kwargs = {"linewidth":5}, axes = axs[idx], edge_threshold='20%', colorbar = True)

  a3 = patches.FancyArrowPatch((20, 80), (80, 20),connectionstyle="arc3,rad=.15")
  axs[idx].add_artist(a3)

  arrow = patches.FancyArrowPatch(
  posA=(0, 0), posB=(1, 0), fc=None, ec='red', color='red',
  arrowstyle='simple, head_width=10, head_length=20, tail_width=0.0',
  connectionstyle="arc3,rad=.15"
  )
  axs[idx].add_artist(arrow)
  axs[idx].add_patch(arrow)



  axs[idx].set_title(instring)


coordinates = np.array([[0, 77, 0],
                        [5, 47, 0],
                        [0, -29, 0]])
coordinates2 = np.array([[4, 77, 0],
                        [9, 47, 0],
                        [4, -29, 0]])
                                                
attack = scipy.io.loadmat('attack_.mat') #load data from the directory
normal = scipy.io.loadmat('normal_.mat') #load data from the directory



fig, axs = plt.subplots(1,2, figsize = (10,5))

pltEffCon(attack['fval'], 'attack', 0)
# pltEffCon(normal['fval'], 'normal', 1)

arrow = patches.FancyArrowPatch(
posA=(-50, -50), posB=(50, 50), fc=None, ec='red', color='red',
arrowstyle='simple, head_width=10, head_length=20, tail_width=0.0',
connectionstyle="arc3,rad=.15"
)
axs[0].add_artist(arrow)
# axs[0].add_artist(a3)
axs[0].add_patch(arrow)




fig.savefig('EFF-CON-UPDATED.svg')