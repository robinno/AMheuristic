# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:46:36 2022

@author: robin
"""

from PARAMS import H, run_in, Allowed_Connections
from GenerateRoutes import generate_route

class Locomotive:    
    def __init__(self, name, location):        
        self.name = name
        self.location = [None for i in range(H + run_in)] 
        self.location[0] = location
        
        self.plan = [140]
        self.route = []
        
        self.front_connected = [None] * Allowed_Connections
        self.back_connected = [None] * Allowed_Connections
        
    def loaded(self):
        for tp in self.front_connected + self.back_connected:
            if tp != None:
                return True
        return False
    
    def Reset(self):
        firstLocation = self.location[0]
        self.location = [None for i in range(H + run_in)]
        self.location[0] = firstLocation
        
        self.front_connected = [None] * Allowed_Connections
        self.back_connected = [None] * Allowed_Connections
        
        
    def update(self, G, DiG, t, Torpedoes):     
        
#        if len(self.plan) == 0:
#            nextTask = naiveSelection()
        
        if len(self.route) == 0 and len(self.plan) > 0:
            print("generating route")
            self.route = generate_route(G, DiG, self, self.location[t-1], self.plan.pop(0))
            print(self.route)
        
        if len(self.route) > 0:
            self.location[t-1] = self.route.pop(0)
            
            
    #static method: select next task in naive way        
    def naiveSelection(Torpedoes):
        # get current task for each tp which requests movement
        tasks = [tp.CurrentTask() for tp in Torpedoes if tp.movementREQ]
        print(tasks)
        
            