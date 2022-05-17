# -*- coding: utf-8 -*-
"""
Created on Mon May 16 16:07:21 2022

@author: robin
"""

from copy import deepcopy
import networkx as nx

from PARAMS import lookAhead, nSwitches
from Locomotive import Locomotive
from ImportNetwork import import_network

def prepare_plan(vehicle, t):
    plan = deepcopy(vehicle.plan) if vehicle.plan != [] else [vehicle.location[t]]
    
    # enlarge to fit length => ASSUMES no plan afterwards!
    while len(plan) < lookAhead: plan.append(plan[-1])
    
    # cut to fit length
    plan = plan[:lookAhead]
    
    return plan
    

def detect_Conflict(plan1, plan2, t):    
    # detection:
    for i in range(1, lookAhead):
        
        # first case:
        if plan1[i] == plan2[i]:
            print("Collision detected, type 1! det on {} for collision on {}".format(t, t+i))
            return i
        
        # second case:
        if plan1[i] == plan2[i+1] and plan1[i+1] == plan2[i]:
            print("Collision detected, type 2! det on {} for collision on {}".format(t, t+i))
            return i
            
        
    return -1 # no collision detected
        
def determine_succ_vehicle(plan1, plan2, i):
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
        
def CASE1_gen_plans(G, continuantPlan, avoidingPlan, switch):
    # set avoidance node for avoiding vehicle
    avNode_candidates = list(G.neighbors(switch))
    
    avNode = None
    while avNode == None:
        n = avNode_candidates.pop(0)
        if n not in continuantPlan:
            avNode = n
            
    # set new route
    newAvPlan = list(nx.shortest_path(G, source = avoidingPlan[0], target = avNode))
    newContPlan = list(nx.shortest_path(G, source = continuantPlan[0], target = switch))[:-1]
    
    # synchronization    
    while len(newAvPlan) < len(newContPlan): newAvPlan.append(newAvPlan[-1])
    while len(newContPlan) < len(newAvPlan): newContPlan.append(newContPlan[-1])
    
    voorsprong = 1
    for i in range(voorsprong): newAvPlan.append(newAvPlan[-1])
    
    # continue route for both new plans:
    newContPlan += list(nx.shortest_path(G, source = newContPlan[-1], target = continuantPlan[-1]))
    newAvPlan += list(nx.shortest_path(G, source = newAvPlan[-1], target = avoidingPlan[-1]))
    
    return newContPlan, newAvPlan  

def CASE2_gen_plans(G, continuantPlan, avoidingPlan, nodeOutOfPlan):
    # set avoidance node for avoiding vehicle
    avNode_candidates = list(G.neighbors(nodeOutOfPlan))
    
    avNode = None
    while avNode == None:
        n = avNode_candidates.pop(0)
        if n not in continuantPlan:
            avNode = n
            
    # set new route
    newAvPlan = list(nx.shortest_path(G, source = avoidingPlan[0], target = avNode))
    newContPlan = continuantPlan
    
    # synchronization    
    while len(newAvPlan) < len(newContPlan): newAvPlan.append(newAvPlan[-1])
    while len(newContPlan) < len(newAvPlan): newContPlan.append(newContPlan[-1])
    
    return newContPlan, newAvPlan  

def CASE3_gen_plans(G, continuantPlan, avoidingPlan, switch):
    # set avoidance node for avoiding vehicle
    avNode_candidates = list(G.neighbors(switch))
    
    avNode = None
    while avNode == None:
        n = avNode_candidates.pop(0)
        if n not in continuantPlan:
            avNode = n
            
    # set new route
    newAvPlan = list(nx.shortest_path(G, source = avoidingPlan[0], target = avNode))
    newContPlan = list(nx.shortest_path(G, source = continuantPlan[0], target = switch))[:-1]
    
    # synchronization    
    while len(newAvPlan) < len(newContPlan): newAvPlan.append(newAvPlan[-1])
    while len(newContPlan) < len(newAvPlan): newContPlan.append(newContPlan[-1])
    
    voorsprong = 0
    for i in range(voorsprong): newAvPlan.append(newAvPlan[-1])
    
    # continue route for both new plans:
    newContPlan += list(nx.shortest_path(G, source = newContPlan[-1], target = continuantPlan[-1]))
    
    return newContPlan, newAvPlan  
    

def generate_plans(G, plan1, plan2, S1, S2, i):
    # determine closest switch => used for avoidance
    currNode1 = plan1[i]
    currNode2 = plan2[i]
    
    case = 1
    
    while currNode1 not in nSwitches and currNode2 not in nSwitches:
        avList1 = list(DiG.successors(currNode1)) if S1 else list(DiG.predecessors(currNode1))
        avList2 = list(DiG.successors(currNode2)) if S2 else list(DiG.predecessors(currNode2))
        
        if avList1 == []:
            if currNode1 in plan2:
                case = 3
        else:
            if currNode1 not in plan2:
                if case != 3:
                    case = 2
                    break
            currNode1 = avList1[0]
            
        if avList2 == []:
            if currNode2 in plan1:
                case = 3
        else:
            if currNode2 not in plan1:
                if case != 3:
                    case = 2
                    break
            currNode2 = avList2[0]
            
    print("case {}: switch node1 = {}, switch node 2 = {}".format(case, currNode1, currNode2))    
        
    newplan1 = newplan2 = []
    
    if case == 1:
        if currNode1 in nSwitches:
            newplan1, newplan2 = CASE1_gen_plans(G, plan1, plan2, currNode1)
        else:
            newplan2, newplan1 = CASE1_gen_plans(G, plan2, plan1, currNode2)
    elif case == 2:
        if currNode1 not in plan2:
            newplan2, newplan1 = CASE2_gen_plans(G, plan2, plan1, currNode1)
        else:
            newplan1, newplan2 = CASE2_gen_plans(G, plan1, plan2, currNode2)
    else:
        if currNode1 not in plan2:
            newplan1, newplan2 = CASE3_gen_plans(G, plan1, plan2, currNode1)
        else:
            newplan2, newplan1 = CASE3_gen_plans(G, plan2, plan1, currNode2)
    
    return newplan1, newplan2


def set_plan_to_train(vehicle, plan, t):
    vehicle.plan = plan
    
    if isinstance(vehicle, Locomotive):
        tps_attached_loco = [tp for tp in vehicle.front_connected+vehicle.back_connected if tp != None]
        
        if tps_attached_loco != []:
            
            pass
    else:
        loco = vehicle.Locomotive
        
        pass
        
def resolve_conflict(G, vehicle1, vehicle2, t):    
    plan1 = prepare_plan(vehicle1, t)
    plan2 = prepare_plan(vehicle2, t)
    
    timeOfCollision = detect_Conflict(plan1, plan2, t)
    
    if timeOfCollision == -1: # no collision detected:
        return False
    
    print("plan 1:", plan1)
    print("plan 2:", plan2)
    
    S1, S2 = determine_succ_vehicle(plan1, plan2, timeOfCollision)
    
    print(S1, S2)
    
    newplan1, newplan2 = generate_plans(G, plan1, plan2, S1, S2, timeOfCollision)
    
    print("new plan 1:", newplan1)
    print("new plan 2:", newplan2)
    
    set_plan_to_train(vehicle1, vehicle2, newplan1, newplan2, t)

    
    
""" TEST CASES """
DiG = import_network()
G = DiG.to_undirected()
    
# first case:
Loco1 = Locomotive("A", 36)
Loco2 = Locomotive("B", 72)
    
Loco1.plan = [36, 132, 71, 121, 120, 119, 118, 117, 116, 115, 70, 69, 114, 72, 113]
Loco2.plan = [72, 114, 69, 70, 115, 116, 117, 118, 119, 120, 121, 71, 132, 36, 172, 173, 35]

Loco1.state = "Pickup"
Loco2.state = "Pickup"

resolve_conflict(G, Loco1, Loco2, 0)
#
## second case:
#Loco1 = Locomotive("A", 168)
#Loco2 = Locomotive("B", 72)
#    
#Loco1.plan = []
#Loco2.plan = [72, 114, 69, 70, 17, 141, 140, 16, 171, 170, 169, 39, 168]
#
#Loco1.state = "Pickup"
#Loco2.state = "Pickup"
#
#resolve_conflict(G, Loco1, Loco2, 0)
#
## third case:
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
#resolve_conflict(G, Loco1, Loco2, 0)