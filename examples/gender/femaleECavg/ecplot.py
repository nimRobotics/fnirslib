import matplotlib.pyplot as plt
from matplotlib.patches import Arc, RegularPolygon, FancyArrowPatch
import numpy as np
from numpy import radians as rad
from matplotlib import cm
import matplotlib
import scipy.io


fig = plt.figure(figsize=(9,9))
ax = plt.gca()
ax.set_aspect('equal')
ax.set_xlim([-50,50])
ax.set_ylim([-120,100])
norm = matplotlib.colors.Normalize(vmin=0, vmax=0.05) #normalize the colorbar

def drawArrow(ax,x0,y0,x1,y1,color_='black'):
    arrow = FancyArrowPatch(
        posA=(x0, y0), posB=(x1, y1), fc=color_, ec=color_,
        arrowstyle='simple, head_width=20, head_length=40, tail_width=0.0',
        connectionstyle="arc3,rad=.15",
        linewidth=7,
        )
    ax.add_artist(arrow)


phase = 'normal'
# phase = 'attack'
data = scipy.io.loadmat(phase+'_.mat') #load data from the directory
f = data['fval'] #fval
s = data['sig'] #sig
pval = data['pval'] #pval
print('\n fval \n',f)
print('\n sig \n',s)
print('\n pval \n',pval)
# replace 0 with NaN
f[s!=1] = np.NaN
print(f)

# x,y coordinates of the regions
coordinates = np.array([[0, 87.75],
                        [0, 11.7],
                        [0, -114.5]])


# mark and label the regions
labels = ["Prefrontal", "Pre Motor & Motor", "Visual"]
print(coordinates[:,0])
ax.scatter(coordinates[:,0], coordinates[:,1], s=250, facecolors='none', edgecolors='black', linewidth=2)
# for i, txt in enumerate(labels):
#     ax.annotate(txt, (coordinates[i,0]+10, coordinates[i,1]), fontsize=20, name="Arial")

# ax.scatter(0,87.45, s=300) # test point

cmap = matplotlib.cm.get_cmap('jet')   # set the color map
norm = matplotlib.colors.Normalize(vmin=0, vmax=0.02)  # normalize the colorbar

# make the arrows for signifcant connections
for i in range(0,f.shape[0]):
    for j in range(0,f.shape[1]):
        if ~np.isnan(f[i,j]):
            print(i,j)
            drawArrow(ax,coordinates[i,0],coordinates[i,1],coordinates[j,0],coordinates[j,1],cmap(norm(f[i,j])))




# add colorbar
from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
cax = divider.append_axes('bottom', size='5%', pad=0.5)
fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap),
             cax=cax, orientation='horizontal', label='Some Units')

# disable the axis
ax.axis('off')

# plt.show()  
# save figure with transparent background
fig.savefig(phase+'.png', transparent=True, bbox_inches='tight', pad_inches=0, dpi=300)

