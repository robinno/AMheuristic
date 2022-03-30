# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 11:53:40 2022

@author: robin
"""

import networkx as nx
import matplotlib.pyplot as plt

def plot_Graph(G, figNum, color_map, node_labels = False, edge_labels = False):
    plt.figure(figNum)
    pos=nx.get_node_attributes(G,'pos')
    nx.draw(G, pos, node_color=color_map, with_labels = node_labels)
    
    if(edge_labels):
        nx.draw_networkx_edge_labels(G, pos)
        
def generate_colormap(G, nG, nD, nRy):
    color_map = []
    for node in G:
        if int(node) in nG:
            color_map.append('red')
        elif int(node) in nD:
            color_map.append('blue')
        elif int(node) in nRy:
            color_map.append('green')
        else:
            color_map.append('black')
            
    return color_map