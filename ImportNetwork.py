# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 11:11:10 2022

@author: robin
"""

import math
import networkx as nx
import matplotlib.pyplot as plt

import Visualise as vis
from PARAMS import nSwitches

def calc_EdgeLength(G, node1, node2):
    posList = nx.get_node_attributes(G,'pos')
    
    (x1,y1) = posList[node1]
    (x2,y2) = posList[node2]
    
    dist = math.sqrt((x1 - x2)**2 + (y1-y2)**2)
    return dist

def load_Switches(G):
    nSwitches.clear()
    
    for n in G.nodes():
        if(len(list(G.neighbors(n))) > 2): # is this node a switch?
            nSwitches.append(n)
           
def rename_nodes(G):    
    for i in range(len(G.nodes())):
        if i not in G.nodes():
            last = sorted(list(G.nodes())).pop()
#            print(last)
            mapping = {last: i}
            G = nx.relabel_nodes(G, mapping)
    
#    print(G.nodes())
    return G
    
def bound(low, high, value):
    return max(low, min(high, value))

def calc_angle(G, posList, previous, current, nb):
    # using θ = cos-1 [ (a · b) / (|a| |b|) ] for the angle
    (px, py) = posList[previous]
    (cx, cy) = posList[current]
    (nbx, nby) = posList[nb]
    
    (ax, ay) = (cx-px, cy-py)
    (bx, by) = (cx-nbx, cy-nby)
    
    dotproduct = ax * bx + ay * by
    lenA = calc_EdgeLength(G, current, previous)
    lenB = calc_EdgeLength(G, current, nb)
    
#    print(dotproduct, lenA, lenB, lenA*lenB)
    
    angle = math.acos(bound(-1,1,dotproduct / (lenA*lenB)))
    
    return angle

def rec_addEdge(G, DiG, previous, current, forward):
    posList = nx.get_node_attributes(G,'pos') 
    nbs = list(G.neighbors(current))
    for nb in nbs:
        if DiG.has_edge(current, nb) or DiG.has_edge(nb, current):
            #edge already present
            continue
        
        angle = calc_angle(G, posList, previous, current, nb)
        
#        print(previous, current, nb, angle)
        
        if(angle < math.pi/2 or angle > 3*math.pi/2): # sharp corner
            if forward:
                DiG.add_edge(nb, current)
                rec_addEdge(G, DiG, current, nb, not(forward))
            else:
                DiG.add_edge(current, nb)
                rec_addEdge(G, DiG, current, nb, not(forward))
        else:
            if forward:
                DiG.add_edge(current, nb)
                rec_addEdge(G, DiG, current, nb, forward)
            else:
                DiG.add_edge(nb, current)
                rec_addEdge(G, DiG, current, nb, forward)
                
        
        
def generate_DiGraph(G):
    DiG = nx.DiGraph()
    posList = nx.get_node_attributes(G,'pos') 
    nodes = list(G.nodes())
    for n in nodes:
        DiG.add_node(n, pos=posList[n])
    
    #starting edge
    previous = 68
    current = 107
    forward = True
    DiG.add_edge(previous, current)
    
    rec_addEdge(G, DiG, previous, current, forward)
    
#    vis.plot_Graph(DiG, 1, [], save = False, node_labels = True)  
    return DiG
    

def import_network(undirected = False):
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
        l = round(calc_EdgeLength(G, n1, n2), 2)
        G.add_edge(n1, n2, length = l)
    
    
    G.remove_nodes_from(list(nx.isolates(G))) # REMOVE UNCONNECTED NODES 
    
    G = rename_nodes(G)
    
    #load the global params
    load_Switches(G)
    
    if not(undirected):
        G = generate_DiGraph(G)
    
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

#G = import_network()

#plt.figure(0)
#pos=nx.get_node_attributes(G,'pos')
#nx.draw(G, pos, node_color='b', font_color = 'w', with_labels = True)
#nx.draw_networkx_edge_labels(G, pos)
#
#remove_intermediary_nodes(G, exempt_nodes)
#
#DiG = generate_DiGraph(G)
#vis.plot_Graph(G, 1, [], save=False, node_labels = True)
#vis.plot_Graph(G, 1, [], save=False, node_labels = False)



""" NOW, fill with discretized nodes """
# TODO
# wacht, is dees nog nodig?


