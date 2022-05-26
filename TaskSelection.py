# -*- coding: utf-8 -*-
"""
Created on Wed May  4 21:27:15 2022

@author: robin
"""
import math

#from ImportNetwork import import_network
#from GenerateSnapshot import generate_TPs, generate_Locos, set_TPlocation
#from ImportTPdata import generateTaskList, importTpData
from GenerateRoutes import PickupNode, DropNode, generate_route_RM
from PARAMS import nD, nRy, nGA, nGA1, nGA2, nGB, nGB1, nGB2
from PARAMS import nWA, nWB, nWo, nWA1, nWA2, nWB1, nWB2, nFA1, nFA2, nFB1, nFB2
from Visualise import plot_Graph2

def addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedolocation, destNode, prio = 0):
    start = Loco.location[t]         
    f1, PL = PickupNode(DiG, torpedolocation)
    f2, finish = DropNode(DiG, destNode)
    
    frontLoad=len([i for i in Loco.front_connected if i != None])
    backLoad=len([i for i in Loco.back_connected if i != None])
    
    RMnodes = [tp.location[t] for tp in Torpedoes]
        
    PickupPath = generate_route_RM(G, DiG, start, PL, 
                                   frontLoad = frontLoad, backLoad = backLoad, 
                                   RMnodes=RMnodes)
    DeliverPath = generate_route_RM(G, DiG, PL, finish, 
                                    frontLoad = frontLoad + int(f1), backLoad = backLoad + int(1-f1), 
                                    RMnodes=RMnodes)
    
    # valid task?
    if len(PickupPath) > 0 and len(DeliverPath) > 0:        
        if f1 != f2: # special case: order reversal needed!!
#            print("order reversal needed !")
#
#            if "-> H" in task.name:
#                print("here")
                
            switchNode = 93
            
            if f1 == True and f2 == False:
                dropLocation = switchNode
                for i in range(frontLoad + 1):
                    dropLocation = list(DiG.predecessors(dropLocation))[0]    
                    
                D1 = generate_route_RM(G, DiG, PL, dropLocation, 
                                       frontLoad = frontLoad + int(f1), backLoad = backLoad + int(1-f1), 
                                       RMnodes=RMnodes)
                    
                pickupLocation = switchNode
                for i in range(backLoad + 1):
                    pickupLocation = list(DiG.successors(pickupLocation))[0] 
                    
                P1 = generate_route_RM(G, DiG, dropLocation, pickupLocation, 
                                       frontLoad = frontLoad, backLoad = backLoad, 
                                       RMnodes=RMnodes)
                D2 = generate_route_RM(G, DiG, pickupLocation, finish, 
                                       frontLoad = frontLoad + int(1-f2), backLoad = backLoad + int(f2), 
                                       RMnodes=RMnodes)
                
                DeliverPath = D1 + [None] + P1 + [None] + D2
                
            elif f1 == False and f2 == True:
                dropLocation = switchNode
                for i in range(backLoad + 1):
                    dropLocation = list(DiG.successors(dropLocation))[0]    
                    
                D1 = generate_route_RM(G, DiG, PL, dropLocation, 
                                       frontLoad = frontLoad + int(f1), backLoad = backLoad + int(1-f1), 
                                       RMnodes=RMnodes)
                    
                pickupLocation = switchNode
                for i in range(frontLoad + 1):
                    pickupLocation = list(DiG.predecessors(pickupLocation))[0] 
                    
                P1 = generate_route_RM(G, DiG, dropLocation, pickupLocation, 
                                       frontLoad = frontLoad + int(f1), backLoad = backLoad + int(1-f1), 
                                       RMnodes=RMnodes + [switchNode])
                D2 = generate_route_RM(G, DiG, pickupLocation, finish, 
                                       frontLoad = frontLoad + int(f1), backLoad = backLoad + int(1-f1), 
                                       RMnodes=RMnodes)
                
                DeliverPath = D1 + [None] + P1 + [None] + D2
        
        Tasklist.append((task, PickupPath, DeliverPath, prio, destNode))

def WZ_destNode_ifAllowed(Torpedoes, currTask, t, nodeList, castingNode = None):
    for i in reversed(range(len(nodeList))):
        currNode = nodeList[i]
        tps_on_node = [tp for tp in Torpedoes if (tp.location[t] == currNode or tp.destNode == currNode) and tp.reserved == False]
        if len(tps_on_node) == 0:
            return currNode
        elif len(tps_on_node) != 0 and i == 0:  #full already
            return None
        
#        tp = tps_on_node[0]
#        if currTask.LST != None and tp.CurrentTask().LST != None and tp.CurrentTask().LST < currTask.LST: #dont block more urgent task
#            return None   
    return None

def available_tasks(G, DiG, t, Loco, Torpedoes, storePic = True):
    Current_movement_tasks = [tp.CurrentTask() for tp in Torpedoes 
                              if tp.CurrentTask() != None and "->" in tp.CurrentTask().name and tp.reserved == False]
    Filling_tasks = [task for tp in Torpedoes for task in tp.tasks if not task.finished and task.name == "Fill"]

    Tasklist = []
    for task in Current_movement_tasks:
        torpedoLocation, prioMvmt = [(tp.location[t], tp.prioMvmt) for tp in Torpedoes if tp.number == task.tp][0]
        
        if task.name == "-> H":
            # waiting positions
            
            # FIRST waiting position:
#            if prioMvmt > 2 and torpedoLocation not in nWo:
            if torpedoLocation not in nWo:
                destNode = WZ_destNode_ifAllowed(Torpedoes, task, t, nWo)
                if destNode != None:
                    addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode, prio = 2)
                
            # SECOND waiting position:
#            if prioMvmt > 1 and len(Filling_tasks) != 0:
            if len(Filling_tasks) != 0:
                CurrentCastingNode = Filling_tasks[0].castingNode
                
                WaitingZone = []
                blockingNode = None
                
                if CurrentCastingNode in nGA1:
                    WaitingZone = nWA1
                    blockingNode = 61
                elif CurrentCastingNode in nGA2:
                    WaitingZone = nWA2
                    blockingNode = 50
                elif CurrentCastingNode in nGB1:
                    WaitingZone = nWB1
                    blockingNode = 90
                else:
                    WaitingZone = nWB2
                    blockingNode = 81
                    
                # filter out self movement:
                if torpedoLocation not in WaitingZone:
                    # Does the blocking hole have a torpedo on it currently?
    #                if len([tp for tp in Torpedoes if tp.location[t] == blockingNode]) == 0:
                        
                    # find the next use of the blocking hole
                    NextHoleUses = [task for task in Filling_tasks if task.castingNode == blockingNode]
                    if len(NextHoleUses) == 0:
                        # add task
                        destNode = WZ_destNode_ifAllowed(Torpedoes, task, t, WaitingZone)
                        if destNode != None:
                            addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode, prio = 1)
                    else:
                        NextHoleUse = NextHoleUses[0]
                        if not(task.LST != None and task.LST >= NextHoleUse.EST): # problem while blocking
                            # add task
                            destNode = WZ_destNode_ifAllowed(Torpedoes, task, t, WaitingZone)
                            if destNode != None:
                                addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode, prio = 1)

            # normal path
            destNode = task.castingNode
            if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                continue 
            
            addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode, prio = 0)
                
        elif task.name == "-> D":
            # waiting positions
            
            # FIRST waiting position:
#            if prioMvmt > 2 and torpedoLocation not in nWo:
            if torpedoLocation not in nWo:
                destNode = WZ_destNode_ifAllowed(Torpedoes, task, t, nWo)
                if destNode != None:
                    addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode, prio = 2)
                
            # SECOND waiting position:
#            if prioMvmt > 1 and len(Filling_tasks) != 0:
            if len(Filling_tasks) != 0:
                CurrentCastingNode = Filling_tasks[0].castingNode
                
                WaitingZone = []
                blockingNode = None
                
                if CurrentCastingNode in nGA1:
                    WaitingZone = nFA1
                    blockingNode = 56
                elif CurrentCastingNode in nGA2:
                    WaitingZone = nFA2
                    blockingNode = 44
                elif CurrentCastingNode in nGB1:
                    WaitingZone = nFB1
                    blockingNode = 86
                else:
                    WaitingZone = nFB2
                    blockingNode = 75
                    
                # filter out self movement:
                if torpedoLocation not in WaitingZone:
                    
                    # Does the blocking hole have a torpedo on it currently?
#                    if len([tp for tp in Torpedoes if tp.location[t] == blockingNode]) == 0:
                        
                    # find the next use of the blocking hole
                    NextHoleUses = [task for task in Filling_tasks if task.castingNode == blockingNode]
                    if len(NextHoleUses) == 0:
                    
                        # add task
                        destNode = WZ_destNode_ifAllowed(Torpedoes, task, t, WaitingZone)
                        if destNode != None:
                            addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode, prio = 1)
                    else:
                        NextHoleUse = NextHoleUses[0]
                        if not(task.LST != None and task.LST >= NextHoleUse.EST): # problem while blocking
                        
                            # add task
                            destNode = WZ_destNode_ifAllowed(Torpedoes, task, t, WaitingZone)
                            if destNode != None:
                                addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode, prio = 1)

            # normal path
            for destNode in nD:
                if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                    continue
                
                addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode, prio = 0)
    
        elif task.name == "-> Ry":
            for destNode in nRy:
                if destNode in [tp.location[t] for tp in Torpedoes]: #node is in use
                    continue
                
                addIfValidTask(G, DiG, Tasklist, task, t, Loco, Torpedoes, torpedoLocation, destNode) 
    
    if len(Tasklist) > 0 and storePic == True:
        plot_Graph2(G, t, Torpedoes, [Loco], save=True, dpi = 100, saveLoc = "keyMoments/")
    
    # Sort the tasklist:
    
    # sort on LST
    Tasklist = sorted(Tasklist, key = lambda i: 1000000000 if i[0].LST == None else i[0].LST)
    # sort on WZ priority
    Tasklist = sorted(Tasklist, key = lambda i: i[3])
    
    return Tasklist

def pick_EDD(G, DiG, t, Loco, Torpedoes, storePic = True):    #select earliest due date 
    AvTasks = available_tasks(G, DiG, t, Loco, Torpedoes, storePic = storePic)

    if len(AvTasks) > 0:
#        print("Loco selecting task at time {}\t -> available tasks: {}".format(t, len(AvTasks)))
#        plot_Graph2(G, t, Torpedoes, [Loco], bigSize=False)
#        print("Available tasks: ", [(t.name, t.tp, wz, dn) for t, x, y, wz, dn in AvTasks])   
        
        #already sorted
        return AvTasks[0] # pick most urgent task

def pick_Age(G, DiG, t, Loco, Torpedoes, storePic = True):  # select the oldest task
    AvTasks = available_tasks(G, DiG, t, Loco, Torpedoes, storePic = storePic)
    if len(AvTasks) > 0:
        # sort on age
        AvTasks = sorted(AvTasks, key = lambda i: i[0].age)
        return AvTasks[0]
    
def pick_Closest(G, DiG, t, Loco, Torpedoes, storePic = True): # select the closest task
    AvTasks = available_tasks(G, DiG, t, Loco, Torpedoes, storePic = storePic)
    if len(AvTasks) > 0:
        # sort on distance of picking
        AvTasks = sorted(AvTasks, key = lambda i: len(i[1]) + len(i[2]))
        return AvTasks[0]
    
def pick(G, DiG, t, Loco, Torpedoes, strat, storePic = True):    
    AvTasks = available_tasks(G, DiG, t, Loco, Torpedoes, storePic = storePic)
    if len(AvTasks) > 0:
        index = math.floor(strat * len(AvTasks))
        return AvTasks[index] # pick the number selected.
    
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
    

    



    