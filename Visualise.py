# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 11:53:40 2022

@author: robin
"""

import networkx as nx
import matplotlib.pyplot as plt
import imageio
from tqdm import tqdm


from PARAMS import nG, nD, nRy, nSwitches, L, T, H

def generate_color_map(G, Locations, UsedTPs = list(range(T)), UsedLocos = list(range(L))):
    color_map = []
    locoPos = []
    tp_pos = []
    
    if(Locations):
        locoPos = [Locations["Loco %d pos"%l] for l in UsedLocos]
        tp_pos = [Locations["TP %d pos"%i] for i in UsedTPs]
    
    for node in G:
        if int(node) in locoPos:
            color_map.append('lime')
        elif int(node) in tp_pos:
            color_map.append('cyan')
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
            
def generate_node_sizes(G, Locations, UsedTPs = list(range(T)), UsedLocos = list(range(L))):
    node_sizes = []
    
    locoPos = []
    tp_pos = []
    
    if(Locations):    
        locoPos = [Locations["Loco %d pos"%l] for l in UsedLocos]
        tp_pos = [Locations["TP %d pos"%i] for i in UsedTPs]
    
    for node in G:          
        if int(node) in locoPos:
            node_sizes.append(1000)
        elif int(node) in tp_pos:
            node_sizes.append(600)
        else:
            node_sizes.append(300)
            
    return node_sizes

def plot_Graph(G, figNum, Locations, UsedTPs = list(range(T)), UsedLocos = list(range(L)), save = False, node_labels = False):
    pos=nx.get_node_attributes(G,'pos')

    color_map = generate_color_map(G, Locations, UsedTPs, UsedLocos)
    node_sizes = generate_node_sizes(G, Locations, UsedTPs, UsedLocos)
    
    plt.figure(figNum)
    
    labeldict = {}
    
    if(Locations):
        for l in UsedLocos:
            labeldict[Locations["Loco %d pos"%l]] = "L%d"%l
        for j in UsedTPs:
            labeldict[Locations["TP %d pos"%j]] = "TP%d"%j

    if(node_labels):
        nx.draw(G, pos, node_color=color_map, node_size = node_sizes, 
                font_color = 'w', with_labels = True)
    else:
        nx.draw(G, pos, node_color=color_map, node_size = node_sizes, 
                font_color = 'w', labels = labeldict)
    
    figure = plt.gcf()
    figure.set_size_inches(25, 15)
    
    if(save):
        plt.savefig("plots/{}.png".format(figNum),  dpi=100)    
        plt.close()
    else:
        plt.show()
        

def generate_GIF(G, Locations):
    
    print("GIF: Generating Frames")
    
    #generate frames
    for t in tqdm(range(H), position=0, leave=True):
        plot_Graph(G, t, Locations[t], save=True)
        
    print("GIF: Importing Frames")
    images = []
    for t in tqdm(range(H), position=0, leave=True):
        images.append(imageio.imread("plots/{}.png".format(t)))
        
    print("GIF: constructing gif")
    imageio.mimsave('GIF/movements.gif', images)
       

    
    
        

