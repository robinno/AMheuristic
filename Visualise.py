# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 11:53:40 2022

@author: robin
"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import imageio

from PARAMS import nG, nD, nRy, nSwitches

def generate_color_map(G, locoPos):
    color_map = []
    
    for node in G:
        if int(node) in locoPos:
            color_map.append('lime')
        elif int(node) in nG:
            color_map.append('red')
        elif int(node) in nD:
            color_map.append('blue')
        elif int(node) in nRy:
            color_map.append('green')
#        elif int(node) in nSwitches:
#            color_map.append('yellow')
        else:
            color_map.append('black')
            
    return color_map
            
def generate_node_sizes(G, locoPos):
    node_sizes = []
    
    for node in G:          
        if int(node) in locoPos:
            node_sizes.append(1000)
        else:
            node_sizes.append(300)
            
    return node_sizes

# TODO split up in functions
def plot_Graph(G, figNum, locoPos, save = False, node_labels = False):
    color_map = generate_color_map(G, locoPos)
    node_sizes = generate_node_sizes(G, locoPos)
    
    plt.figure(figNum)
    pos=nx.get_node_attributes(G,'pos')
    nx.draw(G, pos, node_color=color_map, node_size = node_sizes, 
            font_color = 'w', with_labels = node_labels)
    
    figure = plt.gcf()
    figure.set_size_inches(25, 15)
    
    if(save):
        plt.savefig("plots/{}.png".format(figNum),  dpi=20)    
        plt.close()
    else:
        plt.show()
        
        
def generate_GIF(G, H, locoPositions):
    
    print("GIF: Generating Frames")
    
    #generate frames
    for t in range(H):
        print("current frame: ", t)
        plot_Graph(G, t, locoPositions[t], save=True)
        
    print("GIF: generating GIF")
    images = []
    for t in range(H):
        print("current frame: ", t)
        images.append(imageio.imread("plots/{}.png".format(t)))
        
    imageio.mimsave('GIF/movements.gif', images)
       

    
    
        

