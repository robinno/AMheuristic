# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 11:53:40 2022

@author: robin
"""

import networkx as nx
import matplotlib.pyplot as plt
import imageio
from tqdm import tqdm

from PARAMS import nG, nD, nRy, nSwitches, L, T, H, run_in

def generate_color_map_LOCATIONS(G, Locations, UsedTPs = list(range(T)), UsedLocos = list(range(L))):
    locoPos = [Locations["Loco %d pos"%l] for l in UsedLocos]
    tp_pos = [Locations["TP %d pos"%i] for i in UsedTPs]
    
    return generate_color_map(G, locoPos, tp_pos)

def generate_node_sizes_LOCATIONS(G, Locations, UsedTPs = list(range(T)), UsedLocos = list(range(L))):
    locoPos = [Locations["Loco %d pos"%l] for l in UsedLocos]
    tp_pos = [Locations["TP %d pos"%i] for i in UsedTPs]
    
    return generate_node_sizes(G, locoPos, tp_pos)


def generate_color_map_TORPEDOES(G, t, Torpedoes, Locomotives):
    locoPos = [l.location[t] for l in Locomotives if not (l.location[t] == None)]
    tp_pos = [tp.location[t] for tp in Torpedoes if not (tp.location[t] == None)]
    tp_states = [tp.state[t] for tp in Torpedoes if not (tp.location[t] == None)]
    
    return generate_color_map(G, locoPos, tp_pos, tp_states = tp_states)

def generate_node_sizes_TORPEDOES(G, t, Torpedoes, Locomotives):
    locoPos = [l.location[t] for l in Locomotives if not (l.location[t] == None)]
    tp_pos = [tp.location[t] for tp in Torpedoes if not (tp.location[t] == None)]
    
    return generate_node_sizes(G, locoPos, tp_pos)

def generate_color_map(G, locoPos, tp_pos, tp_states = []):
    color_map = []
    
    for node in G:
        if int(node) in locoPos:
            color_map.append('lime')
        elif int(node) in tp_pos:
            i = tp_pos.index(int(node))
            
            if tp_states[i] == "Full":
                color_map.append('red')
            elif tp_states[i] == "Desulpured":
                color_map.append('orange')
            else:
                color_map.append('green')
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
            
def generate_node_sizes(G, locoPos, tp_pos):
    node_sizes = []
    
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

    color_map = generate_color_map_LOCATIONS(G, Locations, UsedTPs, UsedLocos)
    node_sizes = generate_node_sizes_LOCATIONS(G, Locations, UsedTPs, UsedLocos)
    
    plt.figure(figNum)
    
    labeldict = {}

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
        
def plot_Graph2(G, t, Torpedoes, Locomotives, save = False, bigSize = True, dpi = 20, saveLoc = "plots/"):
    pos=nx.get_node_attributes(G,'pos')

    color_map = generate_color_map_TORPEDOES(G, t, Torpedoes, Locomotives)
    node_sizes = generate_node_sizes_TORPEDOES(G, t, Torpedoes, Locomotives)
    
    labeldict = {}

    for l in Locomotives:
        if(l.location[t] != None):
            labeldict[int(l.location[t])] = "L%s"%l.name
    for tp in Torpedoes:
        if(tp.location[t] != None):
            labeldict[int(tp.location[t])] = "TP%d"%tp.number
#            
#            if tp.state[t] == "Empty":
#                color_map[int(tp.location[t])] = 'green'
#            elif tp.state[t] == "Full":
#                color_map[int(tp.location[t])] = 'red'
#            elif tp.state[t] == "Desulphured":
#                color_map[int(tp.location[t])] = 'orange'

    nx.draw(G, pos, node_color=color_map, node_size = node_sizes, 
            font_color = 'w', labels = labeldict)
    
    
    figure = plt.gcf()
    
    if bigSize:
        figure.set_size_inches(25, 15)
    else:
        figure.set_size_inches(15, 9)
    
    if(save):
        plt.savefig("{}{}.png".format(saveLoc, t), dpi=dpi)    
        plt.close()
    else:
        plt.show()
        

def generate_GIF(G, Locations):
    
    print("GIF: Generating Frames")
    
    #generate frames
    for t in tqdm(range(H + run_in), position=0, leave=True):
        plot_Graph(G, t, Locations[t], save=True)
        
    print("GIF: Importing Frames")
    images = []
    for t in tqdm(range(H+run_in), position=0, leave=True):
        images.append(imageio.imread("plots/{}.png".format(t)))
        
    print("GIF: constructing gif")
    imageio.mimsave('GIF/movements.gif', images)
    
def generate_GIF2(G, Locomotives, Torpedoes, start = 0, end = H + run_in, dpi = 20):
    
    print("GIF: Generating Frames")
    
    #generate frames
    for t in tqdm(range(start, end), position=0, leave=True):
        plot_Graph2(G, t, Torpedoes, Locomotives, save=True, dpi=dpi)
        
    print("GIF: Importing Frames")
    images = []
    for t in tqdm(range(start, end), position=0, leave=True):
        images.append(imageio.imread("plots/{}.png".format(t)))
        
    print("GIF: constructing gif")
    imageio.mimsave('GIF/movements.gif', images)
       

    
    
        

