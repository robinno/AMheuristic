# -*- coding: utf-8 -*-
"""
Created on Sun May  1 22:16:49 2022

@author: robin
"""

from PARAMS import H, run_in

from ImportNetwork import import_network
from ImportTPdata import generate_TPlocations, generate_Locolocations, generateTaskList, importTpData
from Visualise import generate_GIF2


DiG = import_network()
G = DiG.to_undirected()

Torpedoes = generate_TPlocations(DiG)
Locomotives = generate_Locolocations(DiG)

df = importTpData()
Tasks = generateTaskList(G, df, Torpedoes)

for t in range(1, H + run_in):
    movementReq = []
    
    for tp in Torpedoes:
        tp.update(t)
        if tp.movementREQ == True:
            movementReq.append(tp)
    
    for l in Locomotives:
        l.update(G, DiG, t)
        

#interpretation    
generate_GIF2(G, Locomotives, Torpedoes)
    
    
