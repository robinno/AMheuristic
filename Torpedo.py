# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 15:03:56 2022

@author: robin
"""

import pandas as pd

from PARAMS import H, run_in, nD, nRy
#from Task import Task


class Torpedo:      
    
    def __init__(self, number):   
        self.number = number
        self.location = [None for i in range(H + run_in)]
        self.state = ["Empty"]
        self.tasks = []
        
        self.movementREQ = False
        self.taskTimeCounter = 0
        
    def Reset(self):
        for task in self.tasks:
            task.finished = False
        
        firstLocation = self.location[0]
        self.location = [None for i in range(H + run_in)]
        self.location[0] = firstLocation
            
            
    def TaskFinished(self):
        task = self.CurrentTask()
        
        if task.Name == "Fill":
            self.state.append("Full")
        elif task.Name == "Desulphur":
            self.state.append("Desulphured")
        elif task.Name == "Pouring":
            self.state.append("Empty")
        
        self.movementREQ = False
        task.finished = True
        
    def CurrentTask(self):
        todo = [i for i in self.tasks if i.finished == False]
        return None if len(todo) == 0 else todo[0]
    
    def update(self, t):
        if self.taskTimeCounter > 0:
            self.taskTimeCounter -= 1
            if self.taskTimeCounter == 0:
                self.TaskFinished()
        else:
            task = self.CurrentTask()
            
            if task == None:
                return
            
            if "->" in task.name: # movement request
                self.movementREQ = True
                
            elif task.name == "Configure Desulphur" or task.name == "Desulphur":
                if self.location[t-1] in nD:
                    self.taskTimeCounter = task.fixedTime
                else:
                    print("Not at right location!")
            elif task.name == "Configure RyC" or task.name == "Pouring":
                if self.location[t-1] in nRy:
                    self.taskTimeCounter = task.fixedTime
                else:
                    print("Not at right location!")
            elif task.name == "Fill" and t == task.starttime:
                if self.location[t-1] == task.castingNode:
                    self.taskTimeCounter = task.fixedTime
                else:
                    print("Not at right location!")
            else:
                print("Something went wrong with routing!")
            
        
        
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
    