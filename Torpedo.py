# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 15:03:56 2022

@author: robin
"""

import pandas as pd

class Torpedo:
    
    # static method to load data
    # STATIC
    def loadData():
        file = r"torpedoInitialisation.xlsx"
        df = pd.read_excel(file)
        df.set_index("type", inplace = True) # set index column
        return df
    
    def __init__(self, kind):
        df = Torpedo.loadData()
        row = df.loc[kind]
        
        self.kind = kind
        self.typename = row["Typename"]
        self.tarra = row["tarra"]
        self.minNetto = row["minNetto"]
        self.maxNetto = row["maxNetto"]
        self.gemNetto = row["gemNetto"]