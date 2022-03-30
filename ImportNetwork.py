# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 11:11:10 2022

@author: robin
"""

import math
import networkx as nx
import matplotlib.pyplot as plt

import Visualise as vis
from PARAMS import nG, nD, nRy, exempt_nodes

def calc_EdgeLength(G, node1, node2):
    posList = nx.get_node_attributes(G,'pos')
    
    (x1,y1) = posList[node1]
    (x2,y2) = posList[node2]
    
    dist = math.sqrt((x1 - x2)**2 + (y1-y2)**2)
    return dist
    

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
        n1 = int(edge[5])
        n2 = int(edge[6])
        G.add_edge(n1, n2, length = round(calc_EdgeLength(G, n1, n2), 2))
    
    
    G.remove_nodes_from(list(nx.isolates(G))) # REMOVE UNCONNECTED NODES 
    
    return G

#def remove_intermediary_nodes(G, exempt_nodes):
#    nodes = list(G.nodes())
#    
#    for i in range(len(nodes)):    
#        nb = list(G.neighbors(nodes[i]))
#        
#        if len(nb) == 2 and nodes[i] not in exempt_nodes: 
#            newlength = G.get_edge_data(nb[0],nodes[i])['length']
#            newlength += G.get_edge_data(nb[1],nodes[i])['length']
#            
#            G.add_edge(nb[0], nb[1], length = round(newlength, 2))
#            G.remove_node(nodes[i])

""" EXECUTION """

G = import_network()

#plt.figure(0)
#pos=nx.get_node_attributes(G,'pos')
#nx.draw(G, pos, node_color='b')
#nx.draw_networkx_edge_labels(G, pos)
#
#remove_intermediary_nodes(G, exempt_nodes)
#
vis.plot_Graph(G, 1, 15, save=True, node_labels = True)

""" NOW, fill with discretized nodes """
# TODO
# wacht, is dees nog nodig?


