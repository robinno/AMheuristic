# -*- coding: utf-8 -*-
"""
Created on Wed May  4 21:27:15 2022

@author: robin
"""

#from ImportNetwork import import_network
#from GenerateSnapshot import generate_TPs, generate_Locos, set_TPlocation
#from ImportTPdata import generateTaskList, importTpData
from GenerateRoutes import PickupNode, DropNode, generate_route_RM_Unreachables

from PARAMS import nD, nRy, nGA, nGB, nWA, nWB

def addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedolocation, destNode):
    start = Loco.location[t]         
    f1, PL = PickupNode(DiG, torpedolocation)
    f2, finish = DropNode(DiG, destNode)
    
    frontLoad=len([i for i in Loco.front_connected if i != None])
    backLoad=len([i for i in Loco.back_connected if i != None])
        
    PickupPath = generate_route_RM_Unreachables(G, DiG, Loco, start, PL, t, Torpedoes, frontLoad, backLoad)
    DeliverPath = generate_route_RM_Unreachables(G, DiG, Loco, PL, finish, t, Torpedoes, frontLoad + int(f1), backLoad + int(1-f1))
        
    # valid task?
    if len(PickupPath) > 0 and len(DeliverPath) > 0:        
        if f1 != f2: # special case: order reversal needed!!
            print("order reversal needed !")
        
        Tasklist.append((task, PickupPath, DeliverPath))

def available_tasks(G, DiG, t, Loco, Torpedoes):
    Current_movement_tasks = [tp.CurrentTask() for tp in Torpedoes if "->" in tp.CurrentTask().name]

    Tasklist = []
    for task in Current_movement_tasks: 
        torpedoLocation = [tp.location[t] for tp in Torpedoes if tp.number == task.tp][0]
        
        if task.name == "-> H":
            destNode = task.castingNode
            if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                continue 
            
            addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode)
                
        elif task.name == "-> D":
            for destNode in nD:
                if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                    continue
                
                addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode)
    
        elif task.name == "-> Ry":
            for destNode in nRy:
                if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                    continue
                
                addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode) 
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
    

    



    