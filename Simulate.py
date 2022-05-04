# -*- coding: utf-8 -*-
"""
Created on Sun May  1 22:16:49 2022

@author: robin
"""

import pandas as pd

from PARAMS import H, run_in

from ImportNetwork import import_network
from GenerateSnapshot import generate_TPlocations, generate_Locolocations 
from ImportTPdata import generateTaskList, importTpData
from Visualise import generate_GIF2


DiG = import_network()
G = DiG.to_undirected()

Torpedoes = generate_TPlocations(DiG)
Locomotives = generate_Locolocations(DiG)

df = importTpData()
Tasks = generateTaskList(G, df, Torpedoes)

info = []
for t in range(1, H + run_in):
    row = {}
    row["t"] = t
    
    for tp in Torpedoes:
        tp.update(t)
    for l in Locomotives:
        l.update(G, DiG, t, Torpedoes)
        
        
    """ interpretation """
    
    for l in Locomotives:        
        row["loco {} location".format(l.name)] = l.location[t]
        
        
    for tp in Torpedoes:
        row["Tp {} location".format(tp.number)] = tp.location[t]
        row["Tp {} state".format(tp.number)] = tp.state[-1]
        
    info.append(row)
        
infoDF = pd.DataFrame(info)
#generate_GIF2(G, Locomotives, Torpedoes)
    
    
