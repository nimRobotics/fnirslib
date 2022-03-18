import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.io 
import matplotlib.patches as patches

data = scipy.io.loadmat('attack_.mat') #load data from the directory
f = data['fval'] #fval
s = data['sig'] #sig

s_df=pd.DataFrame(s)
f_df=pd.DataFrame(f)

a = np.where(s_df==1)[0]
b = np.where(s_df==1)[1]

Y=[0, 5, 0]
X=[77, 47, -29]
# coordinates = np.array([[0, 77, 0],
#                         [5, 47, 0],
#                         [0, -29, 0]])

plt.axes().set_xlim(-50,50)
plt.axes().set_ylim(-70,70)
plt.axes().set_aspect(1)

#plot circle
for c in range(len(X)):
    circle1=plt.Circle((X[c],Y[c]),0.08,color='r')
    plt.gcf().gca().add_artist(circle1)

f_list=[]
for i in range(0,a.shape[0]):

    f[i]= f_df.loc[a[i],b[i]]
    f_list.append(f[i])
    w = f_df.loc[a[i],b[i]] #assign the intensity of the causality

    #plot arrow
    style = "Simple,  head_width=10, head_length=20"+",tail_width="+str(w)
    kw = dict(arrowstyle=style, color="k")

    a3 = patches.FancyArrowPatch((X[b[i]], Y[b[i]]), (X[a[i]], Y[a[i]]),
                                 connectionstyle="arc3,rad=.15",**kw)
    plt.gca().add_patch(a3)
    
plt.show()