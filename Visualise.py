# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 11:53:40 2022

@author: robin
"""

import networkx as nx

import matplotlib
matplotlib.use("Agg") # turn off interactive plot

import matplotlib.pyplot as plt

import imageio

from PARAMS import nG, nD, nRy

def plot_Graph(G, figNum, locoPos, save = False, node_labels = False):
    color_map = []
    node_sizes = []
    
    for node in G:
        if int(node) == locoPos:
            color_map.append('lime')
        elif int(node) in nG:
            color_map.append('red')
        elif int(node) in nD:
            color_map.append('blue')
        elif int(node) in nRy:
            color_map.append('green')
        else:
            color_map.append('black')
            
        if int(node) == locoPos:
            node_sizes.append(1000)
        else:
            node_sizes.append(300)
    
    plt.figure(figNum)
    pos=nx.get_node_attributes(G,'pos')
    nx.draw(G, pos, node_color=color_map, node_size = node_sizes, 
            font_color = 'w', with_labels = node_labels)
    
    figure = plt.gcf()
    figure.set_size_inches(25, 15)
    
    if(save):
        plt.savefig("plots/{}.png".format(figNum),  dpi=100)
        
    plt.close()
        
        
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
    
    
        

