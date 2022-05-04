# -*- coding: utf-8 -*-
"""
Created on Sun May  1 15:01:53 2022

@author: robin
"""

import networkx as nx
import math

from PARAMS import nGA1, nGA2, nGA, nGB1, nGB2, nGB, nG, nD, nRy, nSwitches
from ImportNetwork import import_network, calc_angle

def count_Dir_Changes(G, path):
    prev, curr = list(path.edges())[0]
    direction = G.has_edge(prev, curr)
    
    dirChanges = 0
    
    for edge in list(path.edges())[1:]:
        prev, curr = edge
        if direction:
            if not G.has_edge(prev,curr):
                direction = not direction
                dirChanges += 1
        else:
            if not G.has_edge(curr,prev):
                direction = not direction
                dirChanges += 1
    
    return dirChanges

# SHORTEST PATH DISTANCES
def calc_Min_Traveltime(G):
    unDirG = G.to_undirected()
    
    MinLengths = {}
    
    # GA -> D
    for start in nGA:
        for end in nD:
            sp = nx.shortest_path(unDirG, source = start, target = end)
            path = nx.path_graph(sp)
            dirChanges = count_Dir_Changes(G, path)
            Minlength = len(sp) + 2 * dirChanges
            MinLengths[(start,end)] = Minlength
            
    # GB -> D
    for start in nGB:
        for end in nD:
            sp = nx.shortest_path(unDirG, source = start, target = end)
            path = nx.path_graph(sp)
            dirChanges = count_Dir_Changes(G, path)
            Minlength = len(sp) + 2 * dirChanges
            MinLengths[(start,end)] = Minlength
            
    # D -> Ry
    for start in nD:
        for end in nRy:
            sp = nx.shortest_path(unDirG, source = start, target = end)
            path = nx.path_graph(sp)
            dirChanges = count_Dir_Changes(G, path)
            Minlength = len(sp) + 2 * dirChanges
            MinLengths[(start,end)] = Minlength
            
    # Ry -> GA
    for start in nRy:
        for end in nGA:
            sp = nx.shortest_path(unDirG, source = start, target = end)
            path = nx.path_graph(sp)
            dirChanges = count_Dir_Changes(G, path)
            Minlength = len(sp) + 2 * dirChanges
            MinLengths[(start,end)] = Minlength    
    
    # Ry -> GB
    for start in nRy:
        for end in nGB:
            sp = nx.shortest_path(unDirG, source = start, target = end)
            path = nx.path_graph(sp)
            dirChanges = count_Dir_Changes(G, path)
            Minlength = len(sp) + 2 * dirChanges
            MinLengths[(start,end)] = Minlength
        
    return MinLengths

def generate_route(G, DiG, l, start, finish):
    path = list(nx.shortest_path(G, source = start, target = finish))
    
    # change path: no sharp angles
    for i in range(1, len(path) - 1):
        n = path[i]
        if n in nSwitches:
            nprev = path[i-1]
            ncurr = n
            nnext = path[i+1]
            
            
            # detect sharp corner
            FtoBchange = DiG.has_edge(nprev, ncurr) and DiG.has_edge(nnext, ncurr)
            BtoFchange = DiG.has_edge(ncurr, nprev) and DiG.has_edge(ncurr, nnext)
            
            if FtoBchange:
                load = 0
#                load = len([i for i in l.back_connected if i != None])
                
                DivertNode = n
                for j in range(load + 1):
                    DivertNode = list(DiG.successors(DivertNode))[0]
                    
                print("Diversion: {} -> {}".format(n, DivertNode))
                
                GoPath = list(nx.shortest_path(G, source = n, target = DivertNode))
                for j in range(len(GoPath)):
                    path.insert(i, GoPath[j])
                    i += 1
                    
                BackPath = list(nx.shortest_path(G, source = DivertNode, target = n))
                for j in range(1, len(BackPath) - 1):
                    path.insert(i, BackPath[j])
                    i += 1
            
            elif BtoFchange:
                load = 0
#               load = len([i for i in l.front_connected if i != None])
                
                DivertNode = n
                for j in range(load + 1):
                    DivertNode = list(DiG.predecessors(DivertNode))[0]
                    
                print("Diversion: {} -> {}".format(n, DivertNode))
                
                GoPath = list(nx.shortest_path(G, source = n, target = DivertNode))
                for j in range(len(GoPath)):
                    path.insert(i, GoPath[j])
                    i += 1
                    
                BackPath = list(nx.shortest_path(G, source = DivertNode, target = n))
                for j in range(1, len(BackPath) - 1):
                    path.insert(i, BackPath[j])
                    i += 1
            
    return path
