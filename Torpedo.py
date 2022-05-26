# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 15:03:56 2022

@author: robin
"""

import pandas as pd

from PARAMS import H, run_in, nD, nRy, suppressOutput
#from Task import Task


class Torpedo:      
    
    def __init__(self, number):   
        self.number = number
        self.location = [None for i in range(H + run_in)]
        self.state = [None for i in range(H + run_in)]
        self.state[0] = "Empty"
        self.tasks = []
        
        self.plan = []
        
        self.Locomotive = None
        self.reserved = False
        self.taskTimeCounter = 0
        
        self.prioMvmt = 100
        self.destNode = None
        
    def reset(self):
        for task in self.tasks:
            task.finished = False
        
        firstLocation = self.location[0]
        self.location = [None for i in range(H + run_in)]
        self.location[0] = firstLocation
        
        self.state = [None for i in range(H + run_in)]
        self.state[0] = "Empty"
        
        self.plan = []
        
        self.Locomotive = None
        self.reserved = False
        self.taskTimeCounter = 0
        
        self.prioMvmt = 100
        self.destNode = None
            
            
    def TaskFinished(self, t):
        task = self.CurrentTask()
        
        if not suppressOutput:
            print("TP {}: finished task {} at time {}".format(self.number, task.name, t))
        
        if task.name == "Fill":
            self.state[t] = "Full"
        elif task.name == "Desulphur":
            self.state[t] = "Desulphured"
        elif task.name == "Pouring":
            self.state[t] = "Empty"
        
        task.finished = True
        task.finishTime = t
        
        self.prioMvmt = 100
        
    def CurrentTask(self):
        todo = [i for i in self.tasks if i.finished == False]
        return None if len(todo) == 0 else todo[0]
    
    def update(self, t):
        self.state[t] = self.state[t-1]
        self.location[t] = self.location[t-1]
        
        # update age task
        task = self.CurrentTask()
        if task != None:
            task.age += 1
        
        # location updating
        if len(self.plan) > 0:
            self.location[t] = self.plan.pop(0)
#            print("Popped location", self.location[t])
        
        # task updating
        if self.taskTimeCounter > 0:
            self.taskTimeCounter -= 1
            if self.taskTimeCounter == 0:
                self.TaskFinished(t)
        else:
            task = self.CurrentTask()
            
            if task == None:
                return
            
            if "->" in task.name:
                # check if at right location:
                if task.name == "-> H":
                    if self.location[t-1] == task.castingNode:
                        self.TaskFinished(t)
                elif task.name == "-> D":
                    if self.location[t-1] in nD:
                        self.TaskFinished(t)
                elif task.name == "-> Ry":
                    if self.location[t-1] in nRy:
                        self.TaskFinished(t)
                
            elif task.name == "Configure D" or task.name == "Desulphur":
                if self.location[t-1] in nD:
                    self.taskTimeCounter = task.fixedTime
                else:
                    raise Exception("Not at right location!")
            elif task.name == "Configure Ry" or task.name == "Pouring":
                if self.location[t-1] in nRy:
                    self.taskTimeCounter = task.fixedTime
                else:
                    raise Exception("Not at right location!")
            elif task.name == "Fill" and t == task.EST:
                if self.location[t-1] == task.castingNode:
                    self.taskTimeCounter = task.fixedTime
                else:
                    raise Exception("Not at right location!")
        
        
    # static method to load data
    # STATIC
#    def loadData():
#        file = r"torpedoInitialisation.xlsx"
#        df = pd.read_excel(file)
#        df.set_index("type", inplace = True) # set index column
#        return df
#    
#    def number(kind):
#        df = Torpedo.loadData()
#        row = df.loc[kind]
#        return row["aantal"]
    
#    def __init__(self, kind):
#        df = Torpedo.loadData()
#        row = df.loc[kind]
#        
#        self.kind = kind
#        self.typename = row["Typename"]
#        self.tarra = row["tarra"]
#        self.minNetto = row["minNetto"]
#        self.maxNetto = row["maxNetto"]
#        self.gemNetto = row["gemNetto"]
    