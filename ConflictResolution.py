# -*- coding: utf-8 -*-
"""
Created on Mon May 16 16:07:21 2022

@author: robin
"""

from copy import deepcopy
import networkx as nx

from PARAMS import lookAhead, nSwitches, suppressOutput
from Locomotive import Locomotive
from Torpedo import Torpedo
from ImportNetwork import import_network
from GenerateRoutes import convertToTProute, generate_route_RM

def prepare_plan(vehicle, t):
    plan = deepcopy(vehicle.plan) if vehicle.plan != [] else [vehicle.location[t]]
    
    Nonepos = 10000
    if None in plan:
        Nonepos = plan.index(None)
    
    # remove things after None
    rest = []
    if None in plan:
        newplan = plan[:plan.index(None)]
        rest = plan[plan.index(None):]
        plan = newplan
    
    if plan != []:
        # enlarge to fit length => ASSUMES no plan afterwards!
        while len(plan) < lookAhead: plan.append(plan[-1])
    
    return plan, rest, Nonepos
    
def beforeNone(plan):
    if None in plan: plan = plan[:plan.index(None)]
    while len(plan) < lookAhead: plan.append(plan[-1])
    return plan

def detect_Conflict(plan1, plan2, t, suppressOutput = False):
    if plan1 == [] or plan2 == []:
        return -1
    
    # detection:
    for i in range(1, lookAhead-1):
        
        # first case:
        if plan1[i] == plan2[i]:
            if not suppressOutput:
                print("Collision detected, type 1! det on {} for collision on {}".format(t, t+i))
            return i
        
        # second case:
        if plan1[i] == plan2[i+1] and plan1[i+1] == plan2[i]:
            if not suppressOutput:
                print("Collision detected, type 2! det on {} for collision on {}".format(t, t+i))
            return i
            
        
    return -1 # no collision detected
        
def determine_succ_vehicle(DiG, plan1, plan2, i):
    
    # first case:
    if plan1[i] == plan2[i]:
        if plan1[i-1] in DiG.successors(plan2[i-1]):
            return True, False
        else:
            return False, True
    
    # second case:
    if plan1[i] == plan2[i+1] and plan1[i+1] == plan2[i]:
        if plan1[i] in DiG.successors(plan2[i]):
            return True, False
        else:
            return False, True
        
def findAvNode(G, DiG, continuantPlan, node, avfrontload = 0, avbackload = 0):
    avNode_candidates = list(G.neighbors(node))
    nb = deepcopy(avNode_candidates)
    
    avNode = None
    while avNode == None:
        if len(avNode_candidates) == 0:
            for i in nb:
                for x in list(G.neighbors(i)):
                    avNode_candidates.append(x)
            nb = deepcopy(avNode_candidates)
        
        n = avNode_candidates.pop(0)
        if n not in continuantPlan:
            avNode = n
            
    # keep track of loads as well!
    
    # determine direction and keep load
    path = list(nx.shortest_path(G, source=node, target=avNode))
    
    if len(path) <= 1:
         # already at right node :) -> dont do anything
         raise Exception("Already at right node?")
         pass
    elif DiG.has_edge(path[0], path[1]):
        # successor case => make sure backload further in plan, o.w. still on switch
        for i in range(avbackload): avNode = list(DiG.successors(avNode))[0]
    else:
        # predecessor case => make sure frontload further in plan, o.w. still on switch
        for i in range(avfrontload): avNode = list(DiG.predecessors(avNode))[0]
    
    if not suppressOutput:
       print("avNode = ", avNode)
    return avNode
        
def CASE1_gen_plans(G, DiG, continuantPlan, avoidingPlan, switch,
                    cfrontload = 0, cbackload = 0, avfrontload = 0, avbackload = 0):
    # set avoidance node for avoiding vehicle
    avNode = findAvNode(G, DiG, continuantPlan, switch, avfrontload = avfrontload, avbackload = avbackload)
    
    # set new route
    newAvPlan = generate_route_RM(G, DiG, avoidingPlan[0], avNode)
    newContPlan = generate_route_RM(G, DiG, continuantPlan[0], switch)
    
    # correct for waiting position:
    successor = False
    if len(newContPlan) < 2:
        if DiG.has_edge(continuantPlan[0], continuantPlan[1]):
            successor = True
    
    elif DiG.has_edge(newContPlan[-2], newContPlan[-1]):
        successor = True
        
    if len(newContPlan) == 0:
        print("problem: newcontplan == 0")
    
    waitingPositionContinuant = 2       
    if successor: # successor
        waitingPositionContinuant += cfrontload + avbackload
    else:
        waitingPositionContinuant += cbackload + avfrontload
        
    offset = min(waitingPositionContinuant, len(newContPlan) - 1)
    if offset > 0:
        newContPlan = newContPlan[:-offset]
    
    # synchronization    
    while len(newAvPlan) < len(newContPlan): newAvPlan.append(newAvPlan[-1])
    while len(newContPlan) < len(newAvPlan): newContPlan.append(newContPlan[-1])
    
    voorsprong = waitingPositionContinuant
    for i in range(voorsprong): newAvPlan.append(newAvPlan[-1])
    
    # continue route for both new plans:
    newContPlan += generate_route_RM(G, DiG, newContPlan[-1], continuantPlan[-1])
    newAvPlan += generate_route_RM(G, DiG, newAvPlan[-1], avoidingPlan[-1])
    
    return newContPlan, newAvPlan  

def CASE2_gen_plans(G, DiG, continuantPlan, avoidingPlan, nodeOutOfPlan,
                    cfrontload = 0, cbackload = 0, avfrontload = 0, avbackload = 0):
    # set avoidance node for avoiding vehicle
    avNode = findAvNode(G, DiG, continuantPlan, nodeOutOfPlan, avfrontload = avfrontload, avbackload = avbackload)
            
    # set new route
    newAvPlan = generate_route_RM(G, DiG, avoidingPlan[0], avNode)
    newContPlan = continuantPlan
    
    return newContPlan, newAvPlan  

def CASE3_gen_plans(G, DiG, continuantPlan, avoidingPlan, switch,
                    cfrontload = 0, cbackload = 0, avfrontload = 0, avbackload = 0):
    # set avoidance node for avoiding vehicle
    avNode = findAvNode(G, DiG, continuantPlan, switch, avfrontload = avfrontload, avbackload = avbackload)
            
    # set new route
    newAvPlan = generate_route_RM(G, DiG, avoidingPlan[0], avNode)
    newContPlan = generate_route_RM(G, DiG, continuantPlan[0], switch)
    
    # correct for waiting position:
    successor = False
    if len(newContPlan) < 2:
        if DiG.has_edge(continuantPlan[0], continuantPlan[1]):
            successor = True
    
    elif DiG.has_edge(newContPlan[-2], newContPlan[-1]):
        successor = True
    
    waitingPositionContinuant = 2
    if successor: # successor
        waitingPositionContinuant += cfrontload + avbackload
    else:
        waitingPositionContinuant += cbackload + avfrontload
        
    offset = min(waitingPositionContinuant, len(newContPlan) - 1)
    if offset > 0:
        newContPlan = newContPlan[:-offset]
        
    # synchronization    
    while len(newAvPlan) < len(newContPlan): newAvPlan.append(newAvPlan[-1])
    while len(newContPlan) < len(newAvPlan): newContPlan.append(newContPlan[-1])
    
    voorsprong = waitingPositionContinuant
    for i in range(voorsprong): newAvPlan.append(newAvPlan[-1])
    
    # continue route for both new plans:
    newContPlan += generate_route_RM(G, DiG, newContPlan[-1], continuantPlan[-1])
    
    return newContPlan, newAvPlan  

def generate_plans(G, DiG, plan1, plan2, S1, S2, i, frontLoad1 = 0, backLoad1 = 0, frontLoad2 = 0, backLoad2 = 0):
    # determine closest switch => used for avoidance
    currNode1 = plan1[i]
    currNode2 = plan2[i]
    
    if len(list(set(plan1[i:]))) > 1 and len(list(set(plan2[i:]))) > 1 :
        # case 1
        case = 1
        while currNode1 not in nSwitches and currNode2 not in nSwitches:
            avList1 = list(DiG.successors(currNode1)) if S1 else list(DiG.predecessors(currNode1))
            avList2 = list(DiG.successors(currNode2)) if S2 else list(DiG.predecessors(currNode2))
    
            currNode1 = currNode1 if len(avList1) == 0 else avList1[0]
            currNode2 = currNode2 if len(avList2) == 0 else avList2[0]
            
            if len(avList1) == 0 and len(avList2) == 0:
                raise Exception("No aversion node!")
    
    else:
        # case 2 or 3
        case = 2
        while currNode1 not in nSwitches and currNode2 not in nSwitches:
            avList1 = list(DiG.successors(currNode1)) if S1 else list(DiG.predecessors(currNode1))
            avList2 = list(DiG.successors(currNode2)) if S2 else list(DiG.predecessors(currNode2))
            
            if avList1 == []:
                if currNode1 in plan2:
                    case = 3
            else:
                if currNode1 not in plan2:
                    if case != 3:
                        break
                currNode1 = avList1[0]
                
            if avList2 == []:
                if currNode2 in plan1:
                    case = 3
            else:
                if currNode2 not in plan1:
                    if case != 3:
                        break
                currNode2 = avList2[0]
                
    if not suppressOutput:
        print("case {}: switch node1 = {}, switch node 2 = {}".format(case, currNode1, currNode2))    
        
    newplan1 = newplan2 = []
    
    if case == 1:
        if currNode1 in nSwitches:
            newplan1, newplan2 = CASE1_gen_plans(G, DiG, plan1, plan2, currNode1, 
                                                 cfrontload = frontLoad1, cbackload = backLoad1, 
                                                 avfrontload = frontLoad2, avbackload = backLoad2)
        else:
            newplan2, newplan1 = CASE1_gen_plans(G, DiG, plan2, plan1, currNode2, 
                                                 cfrontload = frontLoad2, cbackload = backLoad2, 
                                                 avfrontload = frontLoad1, avbackload = backLoad1)
    elif case == 2:
        if currNode1 not in plan2:
            newplan2, newplan1 = CASE2_gen_plans(G, DiG, plan2, plan1, currNode1, 
                                                 cfrontload = frontLoad2, cbackload = backLoad2, 
                                                 avfrontload = frontLoad1, avbackload = backLoad1)
        else:
            newplan1, newplan2 = CASE2_gen_plans(G, DiG, plan1, plan2, currNode2, 
                                                 cfrontload = frontLoad1, cbackload = backLoad1, 
                                                 avfrontload = frontLoad2, avbackload = backLoad2)
    else:
        if currNode1 not in plan2:
            newplan1, newplan2 = CASE3_gen_plans(G, DiG, plan1, plan2, currNode1, 
                                                 cfrontload = frontLoad1, cbackload = backLoad1, 
                                                 avfrontload = frontLoad2, avbackload = backLoad2)
        else:
            newplan2, newplan1 = CASE3_gen_plans(G, DiG, plan2, plan1, currNode2,  
                                                 cfrontload = frontLoad2, cbackload = backLoad2, 
                                                 avfrontload = frontLoad1, avbackload = backLoad1)
    
    return newplan1, newplan2


def get_train(vehicle):
    if isinstance(vehicle, Torpedo):
        Loco = vehicle.Locomotive
    else:
        Loco = vehicle
        
    train = []
    
    back = [Loco.back_connected[i] for i in list(range(Loco.backLoad()))[::-1]] #reversed list
    for i in back:
        train.append(i)
    
    train.append(Loco)     
    
    front = [Loco.front_connected[i] for i in range(Loco.frontLoad())]
    for i in front:
        train.append(i)
        
    return train
            
def set_plan_to_train(G, DiG, vehicle, plan, t):
    train = get_train(vehicle)
    vehicle.plan = plan
    
    if vehicle == train[-1]:
        for index, vehicle in enumerate(train[:-1][::-1]): # reversed list
            vehicle.plan = convertToTProute(G, DiG, t, vehicle.location[t-1], 
                                            succVehicle = train[index + 1], predVehicle = None)
    if vehicle == train[-1]:
        for index, vehicle in enumerate(train[1:]):
            vehicle.plan = convertToTProute(G, DiG, t, vehicle.location[t-1], 
                                            succVehicle = None, predVehicle = train[index - 1])
    
    
def resolve_conflict(G, DiG, F, DiF, Loco1, Loco2, t):   
    train1 = get_train(Loco1)
    train2 = get_train(Loco2)
    
    for i in [True, False]:
        vehicle1 = train1[-1 if i == True else 0]
        front1 = i
    
        vehicle2 = train2[0 if i == True else -1]
        front2 = not i
        
        # swap vehicle if necessary:
        if vehicle1.plan != [] and vehicle2.plan == []:
            temp = vehicle1
            vehicle1 = vehicle2
            vehicle2 = temp
        
        # Check for errors:
        v1End = None
        if vehicle1.plan != []:
            v1End = vehicle1.plan[-1]
        
        v2End = None
        if vehicle2.plan != []:
            v2End = vehicle2.plan[-1]
                
        # prepare plans
        plan1, rest1, Nonepos1 = prepare_plan(vehicle1, t)
        plan2, rest2, Nonepos2 = prepare_plan(vehicle2, t)
        
        
        # Check for errors:
#        v1End = None
#        if len(set(plan1)) > 1:
#            v1End = plan1[-1]
#        
#        v2End = None
#        if len(set(plan2)) > 1:
#            v2End = plan2[-1]
        
        timeOfCollision = detect_Conflict(plan1, plan2, t, suppressOutput = suppressOutput)
        
        if timeOfCollision == -1: # no collision detected:
            continue
        elif i >= Nonepos1 or i >= Nonepos2:
            continue
            
    
        S1, S2 = determine_succ_vehicle(DiF, plan1, plan2, timeOfCollision)
        
        if not suppressOutput:
            print(front1, S1, " and ", front2, S2)
        
        if S1 != front1 or S2 != front2:            
    
            try:
                newplan1, newplan2 = generate_plans(F, DiF, plan1, plan2, S1, S2, timeOfCollision,
                                                    frontLoad1 = Loco1.frontLoad(), backLoad1 = Loco1.backLoad(), 
                                                    frontLoad2 = Loco2.frontLoad(), backLoad2 = Loco2.backLoad())            
            except:
                raise Exception("!!! Unable to resolve conflict!")
                newplan1 = plan1
                newplan2 = plan2
                
            newplan1 += rest1
            newplan2 += rest2
                
            
            # check for errors:
            if (newplan1[-1] != v1End and v1End != None) or (newplan2[-1] != v2End and v2End != None):
                raise Exception("Ending node changed!")
                        
            set_plan_to_train(G, DiG, vehicle1, newplan1, t)
            set_plan_to_train(G, DiG, vehicle2, newplan2, t)
                        
            break
    
    
""" TEST CASES """
DiG = import_network()
G = DiG.to_undirected()
#    
## first case:
#Loco1 = Locomotive("A", 36)
#Loco2 = Locomotive("B", 72)
#    
#Loco1.plan = [36, 132, 71, 121, 120, 119, 118, 117, 116, 115, 70, 69, 114, 72, 113]
#Loco2.plan = [72, 114, 69, 70, 115, 116, 117, 118, 119, 120, 121, 71, 132, 36, 172, 173, 35]
#
#Loco1.state = "Pickup"
#Loco2.state = "Pickup"
#
#resolve_conflict(G, DiG, G, DiG, Loco1, Loco2, 0)
#
# second case:
#Loco1 = Locomotive("A", 168)
#Loco2 = Locomotive("B", 72)
#    
#Loco1.plan = []
#Loco2.plan = [72, 114, 69, 70, 17, 141, 140, 16, 171, 170, 169, 39, 168]
#
#Loco1.state = "Pickup"
#Loco2.state = "Pickup"
#
#resolve_conflict(G, DiG, G, DiG, Loco1, Loco2, 0)
#
# third case:
#DiG.remove_node(167)
#G = DiG.to_undirected()
#
#Loco1 = Locomotive("A", 168)
#Loco2 = Locomotive("B", 72)
#    
#Loco1.plan = []
#Loco2.plan = [72, 114, 69, 70, 17, 141, 140, 16, 171, 170, 169, 39, 168]
#
#Loco1.state = "Pickup"
#Loco2.state = "Pickup"
#
#resolve_conflict(G, DiG, G, DiG, Loco1, Loco2, 0)

# extra test case 2
#Loco1 = Locomotive("A", 71)
#Loco2 = Locomotive("B", 157)
#    
#Loco1.plan = [71, 131, 93, 128, 95, 77, 95, 130, 96, 94, 133, 36, 41, 40, 35, 0, 33, 156, 157, 23]
#Loco2.plan = []
#
#Loco1.state = "Pickup"
#Loco2.state = "Pickup"
#
#resolve_conflict(G, DiG, G, DiG, Loco1, Loco2, 0)

