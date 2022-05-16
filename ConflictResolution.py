# -*- coding: utf-8 -*-
"""
Created on Mon May 16 16:07:21 2022

@author: robin
"""

from copy import deepcopy

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
        
def determine_avoiding_vehicle():
    pass

def resolve_conflict(vehicle1, vehicle2, t):    
    plan1 = prepare_plan(vehicle1, t)
    plan2 = prepare_plan(vehicle2, t)
    
    timeOfCollision = detect_Conflict(plan1, plan2, t)
    
    if timeOfCollision == -1: # no collision detected:
        return False
    
    
    
    
# test case:
DiG = import_network()
G = DiG.to_undirected()
    
Loco1 = Locomotive("A", 36)
Loco2 = Locomotive("B", 72)
    
Loco1.plan = [36, 132, 71, 121, 120, 119, 118, 117, 116, 115, 70, 69, 114, 72, 113]
Loco2.plan = [72, 114, 69, 70, 115, 116, 117, 118, 119, 120, 121, 71, 132, 36, 172, 173, 35, 175]

Loco1.state = "Pickup"
Loco2.state = "Pickup"

resolve_conflict(Loco1, Loco2, 0)