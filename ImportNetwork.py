# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 11:11:10 2022

@author: robin
"""

import networkx as nx
import matplotlib.pyplot as plt

import Visualise as vis
from PARAMS import nG, nD, nRy, exempt_nodes


def import_network():
    f = open('tsc.msh', 'r')
    content = f.read()
    content = content.splitlines()
    
    #split on space
    for i in range(len(content)):
        content[i] = content[i].split()
    
    # get list of nodes and edges
    start = content.index(['$Nodes'])
    end = content.index(['$EndNodes'])
    nodes = content[start+2:end]
    
    start = content.index(['$Elements'])
    end = content.index(['$EndElements'])
    edges = content[start+2:end]
    
    #filter self looping edges
    fEdges = list(filter(lambda c : c[1] != '15', edges))
    
    """ ADD TO NETWORK """
    G = nx.Graph()
    
    # add nodes
    for node in nodes:
        G.add_node(int(node[0]), pos=(float(node[1]), float(node[2])))
        
    # add edges
    for edge in fEdges:
        G.add_edge(int(edge[5]), int(edge[6]), length = int(edge[3]))
    
    
    G.remove_nodes_from(list(nx.isolates(G))) # REMOVE UNCONNECTED NODES 
    
    return G

def remove_intermediary_nodes(G, exempt_nodes):
    nodes = list(G.nodes())
    
    for i in range(len(nodes)):    
        nb = list(G.neighbors(nodes[i]))
        
        if len(nb) == 2 and nodes[i] not in exempt_nodes: 
            newlength = G.get_edge_data(nb[0],nodes[i])['length']
            newlength += G.get_edge_data(nb[1],nodes[i])['length']
            
            G.add_edge(nb[0], nb[1], length = newlength)
            G.remove_node(nodes[i])
    

""" EXECUTION """

G = import_network()

plt.figure(0)
pos=nx.get_node_attributes(G,'pos')
nx.draw(G, pos, node_color='b')

remove_intermediary_nodes(G, exempt_nodes)

vis.plot_Graph(G, 1, vis.generate_colormap(G, nG, nD, nRy), node_labels = True)

""" NOW, fill with discretized nodes """
tp_length = 40

pass # TODO


