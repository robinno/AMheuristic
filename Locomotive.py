# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:46:36 2022

@author: robin
"""

from PARAMS import H, run_in, Allowed_Connections, connect_slots
from GenerateRoutes import convertToTProute
from TaskSelection import EDD

class Locomotive:    
    def __init__(self, name, location):        
        self.name = name
        self.location = [None for i in range(H + run_in)] 
        self.location[0] = location
        
        self.plan = []
        self.DeliverPath = []
        
        self.connectionCounter = 0
        
        self.front_connected = [None] * Allowed_Connections
        self.back_connected = [None] * Allowed_Connections
        
        self.state = "Drive"
        self.task = None
        
        self.prioMvmt = 100
        
        #for the genetic algorithm
#        self.choosingPlan = [("Pick", 0) for i in range()]
        
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
            taskPack = EDD(G, DiG, t, self, Torpedoes)
            
            if(taskPack) != None:
                self.task, self.plan, self.DeliverPath, self.prioMvmt,  destNode = taskPack
                torpedo = [i for i in Torpedoes if i.number == self.task.tp][0]
                torpedo.reserved = True
                torpedo.destNode = destNode
                print("Task: ", self.task.name, self.task.tp, self.prioMvmt)
            
            self.state = "Pickup"
    
        if self.state == "Pickup":
            if(len(self.plan) > 0):
                self.location[t] = self.plan.pop(0)
                
                if self.location[t] == None:
                    self.location[t] = self.location[t-1]
                    self.state = "Connect"
                    self.connectionCounter = connect_slots
            else:
                self.state = "Connect"
                self.connectionCounter = connect_slots
        
        elif self.state == "Connect":
            
            if(self.connectionCounter > 0):
                self.connectionCounter -= 1 
            else:
                self.state = "Deliver"
                torpedo = [i for i in Torpedoes if i.number == self.task.tp][0]
                torpedo.Locomotive = self
                
                self.plan = self.DeliverPath
                
                #TODO: fix below
                if torpedo.location[t-1] in list(DiG.predecessors(self.location[t])):
                    self.back_connected[0] = torpedo
                    torpedo.plan = convertToTProute(G, DiG, t, torpedo.location[t-1], succVehicle = self, predVehicle = None)
                    torpedo.prioMvmt = self.prioMvmt
                elif torpedo.location[t-1] in list(DiG.successors(self.location[t])):
                    self.front_connected[0] = torpedo
                    torpedo.plan = convertToTProute(G, DiG, t, torpedo.location[t-1], succVehicle = None, predVehicle = self)
                    torpedo.prioMvmt = self.prioMvmt
                else:
                    raise Exception("!! Problem: no torpedo next to loco !!")
                    self.front_connected[0] = torpedo
        
        elif self.state == "Deliver":
            if len(self.plan) > 0:
                # move loco:
                self.location[t] = self.plan.pop(0)
                
                if self.location[t] == None:
                    self.location[t] = self.location[t-1]
                    self.state = "Disconnect"
                    self.connectionCounter = connect_slots
            else:
                self.state = "Disconnect"
                self.connectionCounter = connect_slots
            
        elif self.state == "Disconnect":
            torpedo = [i for i in Torpedoes if i.number == self.task.tp][0]
            
            if(self.connectionCounter > 0):
                self.connectionCounter -= 1 
            else:
                if len(self.plan) > 0:
                    # still a pickup action to do!
                    self.state = "Pickup"
                else:
                    self.state = None
                    self.task = None
                
                torpedo.Locomotive = None
                torpedo.reserved = False
                torpedo.destNode = None
                self.back_connected[0] = None
                self.front_connected[0] = None
        
        
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
        
            