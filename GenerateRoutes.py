# -*- coding: utf-8 -*-
"""
Created on Sun May  1 15:01:53 2022

@author: robin
"""

import networkx as nx

from PARAMS import nWA, nWo, nGA, nGB, nD, nRy, nSwitches

# returns TRUE if connected to the front of the train
def PickupNode(DiG, node, dist = 1):
    pred = node in nWA + nGA + nRy + nWo
    
    for i in range(dist):
        if pred:
            node = list(DiG.predecessors(node))[0]
        else:
            node = list(DiG.successors(node))[0]
        
    return pred, node
  
# returns TRUE if connected to the front of the train
def DropNode(DiG, node, dist = 1):
    pred = node in nWA + nGA + nD + nWo
    
    for i in range(dist):
        if pred:
            node = list(DiG.predecessors(node))[0]
        else:
            node = list(DiG.successors(node))[0]
        
    return pred, node

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

def generate_route(G, DiG, start, finish, frontLoad = 0, backLoad = 0):
    try:
        path = list(nx.shortest_path(G, source = start, target = finish))
    except:
#        print(start, finish)
#        nx.draw(G, nx.get_node_attributes(G,'pos'), with_labels = True)
#        raise Exception("Check eens je grafieken?")
        return []
    
    # change path: no sharp angles
    for i in range(1, len(path) - 1):
        n = path[i]
        if n in nSwitches:
            nprev = path[i-1]
            ncurr = n
            nnext = path[i+1]
            
            if nprev == nnext: # would mean we dont need to switch the track
                continue
            
            # detect sharp corner
            FtoBchange = DiG.has_edge(nprev, ncurr) and DiG.has_edge(nnext, ncurr)
            BtoFchange = DiG.has_edge(ncurr, nprev) and DiG.has_edge(ncurr, nnext)
            
            DivertNode = n
            
            if FtoBchange:        
                for j in range(backLoad + 1):
#                    print("Problem with backload ? : ", backLoad, DivertNode)
                    DivertNode = list(DiG.successors(DivertNode))[0]
                    
            elif BtoFchange:
                for j in range(frontLoad + 1):
                    DivertNode = list(DiG.predecessors(DivertNode))[0]
                    
            if FtoBchange or BtoFchange:
                # add the diversion:            
#                print("Diversion: {} -> {}".format(n, DivertNode))
                    
                GoPath = list(nx.shortest_path(G, source = n, target = DivertNode))
                for j in range(len(GoPath)):
                    path.insert(i, GoPath[j])
                    i += 1
                    
                BackPath = list(nx.shortest_path(G, source = DivertNode, target = n))
                for j in range(1, len(BackPath) - 1):
                    path.insert(i, BackPath[j])
                    i += 1
            
    return path

def generate_route_RM(G, DiG, start, finish, frontLoad = 0, backLoad = 0, RMnodes = []):
    H = G.copy()
    DiH = DiG.copy()
        
    for node in RMnodes:
        H.remove_node(node)
        DiH.remove_node(node)
            
    return generate_route(H, DiH, start, finish, frontLoad = frontLoad, backLoad = backLoad)

def convertToTProute(G, DiG, t, vLoc, succVehicle = None, predVehicle = None):
    
    if succVehicle != None:
        sPlan = succVehicle.plan
        
        if None in sPlan:
            sPlan = succVehicle.plan[:succVehicle.plan.index(None)]
        
        plan = [None] * len(sPlan)
        currLocation = vLoc

        for index, node in enumerate(sPlan):
            nextNodeList = list(DiG.predecessors(node))
            neighbors = list(G.neighbors(currLocation))
                
            candidates = [i for i in nextNodeList if i in neighbors]
            
            n = nextNodeList[0]
            
            if len(nextNodeList) > 1: # special case
                for n_candidate in candidates:
                    if n_candidate in sPlan[index:]:
                        n = n_candidate
                        break                              
                
            plan[index] = currLocation = n
        return plan
    elif predVehicle != None:
        pPlan = predVehicle.plan
        
        if None in pPlan:
            pPlan = predVehicle.plan[:predVehicle.plan.index(None)]
        
        plan = [None] * len(pPlan)
        currLocation = vLoc

        for index, node in enumerate(pPlan):
            nextNodeList = list(DiG.successors(node))
            neighbors = list(G.neighbors(currLocation))
                
            candidates = [i for i in nextNodeList if i in neighbors]
            
            n = nextNodeList[0]
            
            if len(nextNodeList) > 1: # special case
                for n_candidate in candidates:
                    if n_candidate in pPlan[index:]:
                        n = n_candidate
                        break
            
            plan[index] = currLocation = n
        return plan
    else:
        raise Exception("both succ and pred vehicle given when generating TP route")
    
    
