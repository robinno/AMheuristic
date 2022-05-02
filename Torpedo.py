# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 15:03:56 2022

@author: robin
"""

import pandas as pd

from PARAMS import H, run_in
#from Task import Task


class Torpedo:      
    
    def __init__(self, number):   
        self.number = number
        self.location = [None for i in range(H + run_in)]
        self.state = ["Empty"]
        self.tasks = []
        
        self.taskTimeCounter = 0
        
    def Reset(self):
        for task in self.tasks:
            task.finished = False
        
        firstLocation = self.location[0]
        self.location = [None for i in range(H + run_in)]
        self.location[0] = firstLocation
            
            
    def TaskFinished(self):
        self.tasks[self.tasks.index(False)] = True
        
    def CurrentTask(self):
        return self.tasks.index(False)
        
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
    