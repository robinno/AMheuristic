# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:46:36 2022

@author: robin
"""

from PARAMS import H, run_in, Allowed_Connections
from GenerateRoutes import generate_route
from TaskSelection import naiveSelection

class Locomotive:    
    def __init__(self, name, location):        
        self.name = name
        self.location = [None for i in range(H + run_in)] 
        self.location[0] = location
        
        self.PickupPath = []
        self.DeliverPath = []
        
        self.connectionCounter = 0
        
        self.front_connected = [None] * Allowed_Connections
        self.back_connected = [None] * Allowed_Connections
        
        self.state = "Drive"
        self.task = None
        
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
        
        self.location[t] = self.location[t-1]
        
        if self.task == None:
            # pick a new task
            taskPack = naiveSelection(G, DiG, t, self, Torpedoes)
            
            if(taskPack) != None:
                self.task, self.PickupPath, self.DeliverPath = taskPack
                print("Task: ", self.task.name, self.task.tp)
                print("Path pickup: ", self.PickupPath)
                print("Path deliver: ", self.DeliverPath)
            
            pass
#            self.state = "Drive"
    
        if self.state == "Drive":
            pass
        elif self.state == "Connect":
            pass
        elif self.state == "Deliver":
            pass
        elif self.state == "Disconnect":
            pass
        
        
#        if len(self.plan) == 0:
#            nextTask = naiveSelection()
        
        # make sure a route is available
#        if len(self.route) == 0 and len(self.plan) > 0:
#            
#            if self.connectionCounter == 0:# connection finished
#                print("generating route")
#                self.route = generate_route(G, DiG, self.location[t-1], self.plan[0])
#                self.route = self.route[1:-1] #pop off first and last element
#                print(self.route)
#        
#        if len(self.route) > 0:
#            self.location[t] = self.route.pop(0)
        
            