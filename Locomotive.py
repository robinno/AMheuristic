# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:46:36 2022

@author: robin
"""

from PARAMS import H, run_in, Allowed_Connections, connect_slots, stratLength, suppressOutput
from GenerateRoutes import convertToTProute
from TaskSelection import pick, pick_EDD, pick_Age, pick_Closest, pick_minDist, pick_Hfirst

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
        
        self.state = "Waiting"
        self.task = None
        
        self.prioMvmt = 100
        
        #for the genetic algorithm
        self.strategy = [("Pick", 0) for i in range(2*stratLength)]
        self.stratIndex = 0
        self.waitCounter = 0
        
    def frontLoad(self):
        return len([i for i in self.front_connected if i != None])
    
    def backLoad(self):
        return len([i for i in self.back_connected if i != None])
        
    def loaded(self):
        for tp in self.front_connected + self.back_connected:
            if tp != None:
                return True
        return False
    
    def reset(self):
        firstLocation = self.location[0]
        self.location = [None for i in range(H + run_in)]
        self.location[0] = firstLocation
        
        self.plan = []
        self.DeliverPath = []
        
        self.connectionCounter = 0
        
        self.front_connected = [None] * Allowed_Connections
        self.back_connected = [None] * Allowed_Connections
        
        self.state = "Waiting"
        self.task = None
        
        self.prioMvmt = 100 
        
        self.stratIndex = 0
        
    def update(self, G, DiG, t, Torpedoes, picking = "strategic", prio = False, storePic = True):
        
        self.location[t] = self.location[t-1]
        
        if self.waitCounter > 0: # if waiting in strategy
            self.waitCounter -= 1
        elif self.task == None:
            if(len(self.plan) > 0): # avoiding plan
                self.location[t] = self.plan.pop(0)
                if self.location[t] == None:
                    self.location[t] = self.location[t-1]
                    
                self.state = "Waiting"
            else:
                if picking == "strategic":
                    if self.stratIndex > len(self.strategy) - 1:
                        raise Exception("Strategy not long enough")
                    
                    #what is current strategy?
                    currStrategy = self.strategy[self.stratIndex]
                    
                    strat = currStrategy[0]
                    number = currStrategy[1]
                    
                    # execute current strategy
                    if strat == "Pick":
                        # pick a new task
                        taskPack = pick(G, DiG, t, self, Torpedoes, number, prio = prio, storePic = storePic)
                        
                        if(taskPack) != None:
                            self.task, self.plan, self.DeliverPath, self.prioMvmt,  destNode = taskPack
                            torpedo = [i for i in Torpedoes if i.number == self.task.tp][0]
                            torpedo.reserved = True
                            torpedo.destNode = destNode
                            if not suppressOutput:
                                print("Task: ", self.task.name, self.task.tp, self.prioMvmt)
                            
                            self.stratIndex += 1
                    
                            self.state = "Pickup"
                    elif strat == "Wait":
                        self.waitCounter = number
                        self.stratIndex += 1
                    else:
                        raise Exception("Unknown picking option")
                
                else:
                    taskPack = None
                    
                    if picking == "EDD":
                        taskPack = pick_EDD(G, DiG, t, self, Torpedoes, prio = prio, storePic = storePic)
                    elif picking == "age":
                        taskPack = pick_Age(G, DiG, t, self, Torpedoes, prio = prio, storePic = storePic)
                    elif picking == "closest":
                        taskPack = pick_Closest(G, DiG, t, self, Torpedoes, prio = prio, storePic = storePic)
                    elif picking == "minDist":
                        taskPack = pick_minDist(G, DiG, t, self, Torpedoes, prio = prio, storePic = storePic)
                    elif picking == "Hfirst":
                        taskPack = pick_Hfirst(G, DiG, t, self, Torpedoes, prio = prio, storePic = storePic)
                    else:
                        raise Exception("Unknown strategy")
                    
                    if(taskPack) != None:
                        self.task, self.plan, self.DeliverPath, self.prioMvmt,  destNode = taskPack
                        torpedo = [i for i in Torpedoes if i.number == self.task.tp][0]
                        torpedo.reserved = True
                        torpedo.destNode = destNode
                        if not suppressOutput:
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
                torpedo = [i for i in Torpedoes if i.number == self.task.tp][0]
                if self.location[t] in list(G.neighbors(torpedo.location[t-1])):
                    self.state = "Connect"
                    self.connectionCounter = connect_slots
                else:
                    raise Exception("Pickup plan finished but not next to TP")
        
        elif self.state == "Connect":
            if(self.connectionCounter > 0):
                self.connectionCounter -= 1 
            else:
                self.state = "Deliver"
                torpedo = [i for i in Torpedoes if i.number == self.task.tp][0]
                torpedo.Locomotive = self
                
                self.plan = self.DeliverPath
                
                #TODO: fix below for multiple tps
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
                    torpedo.reserved = True # still reserved!!
                else:
                    self.state = "Waiting"
                    self.task = None
                    torpedo.reserved = False
                
                torpedo.Locomotive = None
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
        
            