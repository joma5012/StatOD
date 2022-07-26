from operator import imod
import matplotlib.pyplot as plt
import pickle
import numpy as np
import os
from GravNN.Visualization.VisualizationBase import VisualizationBase
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.ticker as mticker
import StatOD

from GravNN.CelestialBodies.Asteroids import Eros

class MathTextSciFormatter(mticker.Formatter):
    def __init__(self, fmt="%1.2e"):
        self.fmt = fmt
    def __call__(self, x, pos=None):
        s = self.fmt % x
        decimal_point = '.'
        positive_sign = '+'
        tup = s.split('e')
        significand = tup[0].rstrip(decimal_point)
        sign = tup[1][0].replace(positive_sign, '')
        exponent = tup[1][1:].lstrip('0')
        if exponent:
            exponent = '10^{%s%s}' % (sign, exponent)
        if significand and exponent:
            s =  r'%s{\times}%s' % (significand, exponent)
        else:
            s =  r'%s%s' % (significand, exponent)
        return "${}$".format(s)

def plot_3d(rVec, traj_cm=plt.cm.jet, solid_color=None, reverse_cmap=False, **kwargs):

    ax = plt.gca()
    rx = [rVec[0]]
    ry = [rVec[1]]
    rz = [rVec[2]]

    label = kwargs.get('label', None)
    legend = kwargs.get('legend', None)
    linewidth = kwargs.get('linewidth', None)
    # if there is a cmap specified, break the line into segments
    # and vary the color to show time evolution
    if traj_cm is not None and solid_color is None:
        N = len(rx[0])
        cVec = np.zeros((N,4))
        for i in range(N-1):
            if reverse_cmap:
                cVec[i] = traj_cm(1 - i/N)
            else:
                cVec[i] = traj_cm(i/N)
            ax.plot(rx[0][i:i+2], ry[0][i:i+2], rz[0][i:i+2], 
                    color=cVec[i], alpha=kwargs['line_opacity'], label=label, linewidth=linewidth)
    else:
        # Just plot a line, gosh.
        if solid_color is None:
            solid_color = 'black'
        ax.plot(rx[0], ry[0], rz[0], c=solid_color, alpha=kwargs['line_opacity'], label=label, linewidth=linewidth)

    maxVal = max([max(np.abs(np.concatenate((plt.gca().get_xlim(), rx[0])))), 
                  max(np.abs(np.concatenate((plt.gca().get_ylim(), ry[0])))), 
                  max(np.abs(np.concatenate((plt.gca().get_zlim(), rz[0]))))])
    minVal =  -maxVal

    ax.set_xlim(minVal, maxVal)
    ax.set_ylim(minVal, maxVal)
    ax.set_zlim(minVal, maxVal)

    ax.set_xlabel('x')
    ax.set_ylabel('y')

    ax.xaxis.set_major_formatter(MathTextSciFormatter("%1.0e"))
    ax.yaxis.set_major_formatter(MathTextSciFormatter("%1.0e"))
    ax.zaxis.set_major_formatter(MathTextSciFormatter("%1.0e"))
    
    # ax.view_init(90, 30)
    ax.view_init(45, 45)
    plt.tight_layout()

    return ax

def plot_cartesian_state_3d(X, obj_file=None, **kwargs):
    """Plot the cartesian state vector in subplots

    Args:
        t (np.array): time vector
        X (np.array): state vector [N x 6]
    """
    options = {
        "cmap" : plt.cm.winter,
        "plot_start_point" : True,
        "new_fig" : True,
        "line_opacity" : 1.0,
        }
    options.update(kwargs)

    if options["new_fig"]:
        vis = VisualizationBase(formatting_style='AIAA')
        fig, ax = vis.new3DFig(**kwargs)
    else:
        ax = plt.gca()

    plot_3d(X[:,0:3].T, obj_file=obj_file, traj_cm=options['cmap'], **options) 

    # Import the asteroid shape model if appropriate. 
    if obj_file is not None:
        import trimesh
        filename, file_extension = os.path.splitext(obj_file)
        mesh = trimesh.load_mesh(obj_file, file_type=file_extension[1:])
        cmap = plt.get_cmap('Greys')
        tri = Poly3DCollection(mesh.triangles*1000, cmap=cmap, facecolors=cmap(128), alpha=0.5)
        p = plt.gca().add_collection3d(tri)

    if options['plot_start_point']:
        plt.gca().scatter(X[0,0], X[0,1], X[0,2], s=3, c='r')

def main():

    vis = VisualizationBase(save_directory=StatOD.__path__[0] + "/../Plots/")
    with open("Data/Trajectories/trajectory_asteroid.data", 'rb') as f:
        data = pickle.load(f)
    
    plot_cartesian_state_3d(data['X']*1E3, Eros().obj_8k)     

    vis.save(plt.gcf(), "spacecraft_trajectory.pdf")   
    plt.show()
    
if __name__ == "__main__":
    main()