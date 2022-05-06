# -*- coding: utf-8 -*-
"""
Created on Wed May  4 21:27:15 2022

@author: robin
"""

#from ImportNetwork import import_network
#from GenerateSnapshot import generate_TPs, generate_Locos, set_TPlocation
#from ImportTPdata import generateTaskList, importTpData
from GenerateRoutes import generate_route_RM_Unreachables

from PARAMS import nD, nRy, nGA, nGB, nWA, nWB

def available_tasks(G, DiG, t, Loco, Torpedoes):
    Current_movement_tasks = [tp.CurrentTask() for tp in Torpedoes if "->" in tp.CurrentTask().name]

    Tasklist = []
    for task in Current_movement_tasks: 
        torpedoLocation = [tp.location[t] for tp in Torpedoes if tp.number == task.tp][0]
        
        if task.name == "-> H":
            destNode = task.castingNode
            if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                continue            
            # pickup path
            start = Loco.location[t]            
            PL = None
            finish = None
        
            if torpedoLocation in nWA:
                PL = list(DiG.successors(torpedoLocation))[0]
            elif torpedoLocation in nWB:
                PL = list(DiG.predecessors(torpedoLocation))[0]
            else:
                PL = list(DiG.successors(torpedoLocation))[0]
                
            PickupPath = generate_route_RM_Unreachables(G, DiG, start, PL, t, Torpedoes)    
            
            # deliver path                
            if destNode in nGA:
                finish = list(DiG.successors(destNode))[0]
            else:
                finish = list(DiG.predecessors(destNode))[0]
            
            DeliverPath = generate_route_RM_Unreachables(G, DiG, PL, finish, t, Torpedoes)
            
            # valid task?
            if len(PickupPath) > 0 and len(DeliverPath) > 0:
                Tasklist.append((task, PickupPath, DeliverPath))
                
                
        elif task.name == "-> D":
            for destNode in nD:
                if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                    continue
                
                # pickup path
                start = Loco.location[t] 
                PL = None
                
                if torpedoLocation in nGA + nWA:
                    PL = list(DiG.successors(torpedoLocation))[0]
                elif torpedoLocation in nGB + nWB:
                    PL = list(DiG.predecessors(torpedoLocation))[0]
                
                PickupPath = generate_route_RM_Unreachables(G, DiG, start, PL, t, Torpedoes)  
                
                # deliver path
                finish = list(DiG.predecessors(destNode))[0]
                
                DeliverPath = generate_route_RM_Unreachables(G, DiG, PL, finish, t, Torpedoes)
                
                 # valid task?
                if len(PickupPath) > 0 and len(DeliverPath) > 0:
                     Tasklist.append((task, PickupPath, DeliverPath))
    
        elif task.name == "-> Ry":
            for destNode in nRy:
                if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                    continue
                
                # pickup path
                start = Loco.location[t] 
                
                PL = list(DiG.successors(torpedoLocation))[0]
                
                PickupPath = generate_route_RM_Unreachables(G, DiG, start, PL, t, Torpedoes)  
                
                # deliver path
                finish = list(DiG.successors(destNode))[0]
                
                DeliverPath = generate_route_RM_Unreachables(G, DiG, PL, finish, t, Torpedoes)
                
                 # valid task?
                if len(PickupPath) > 0 and len(DeliverPath) > 0:
                     Tasklist.append((task, PickupPath, DeliverPath))       
    return Tasklist



def naiveSelection(G, DiG, t, Loco, Torpedoes):    
    AvTasks = available_tasks(G, DiG, t, Loco, Torpedoes)
    
    if len(AvTasks) > 0:
        return AvTasks[0]
    else:
        return None

#DiG = import_network()
#G = DiG.to_undirected()
#
#df = importTpData()
#Tasks = generateTaskList(G, df)
#
#Torpedoes = generate_TPs(Tasks)
#set_TPlocation(DiG, df, Torpedoes)
#Locomotives = generate_Locos(DiG)
#    
#naiveSelection(G, DiG, t, Torpedoes)
    

    



    