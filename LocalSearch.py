# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 17:48:46 2022

@author: robin
"""

from PARAMS import H, timestep
from ImportTPdata import importTpData, generate_TPlocations, generateTaskList
from ImportNetwork import import_network
    
df = importTpData()
G = import_network()
Torpedoes = generate_TPlocations(G)

Tasklist = generateTaskList(G, df, Torpedoes)