# -*- coding: utf-8 -*-
"""
Created on Sun May  1 22:16:49 2022

@author: robin
"""

import pandas as pd
import traceback
from tqdm import tqdm
import os
import glob

from PARAMS import H, run_in

from ImportNetwork import import_network
from GenerateSnapshot import generate_TPs, generate_Locos, set_TPlocation
from ImportTPdata import generateTaskList, importTpData
from Visualise import generate_GIF2

# clear plot folders:
files = glob.glob('keyMoments/*.png')
for f in files:
    os.remove(f)
    
files = glob.glob('plots/*.png')
for f in files:
    os.remove(f)

DiG = import_network()
G = DiG.to_undirected()

df = importTpData()
Tasks = generateTaskList(G, df)

Torpedoes = generate_TPs(Tasks)
set_TPlocation(DiG, df, Torpedoes)
Locomotives = generate_Locos(DiG)

#interpretation
info = []
row = {}
row["t"] = 0
for l in Locomotives:
    row["loco {} location".format(l.name)] = l.location[0]

for tp in Torpedoes:
    row["Tp {} location".format(tp.number)] = tp.location[0]
    row["Tp {} state".format(tp.number)] = tp.state[-1]
        
info.append(row)

try:
    print("Simulating")
    for t in range(1, H+run_in):#tqdm(range(1, H + run_in), position=0, leave=True):
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
except Exception:
    traceback.print_exc()
        
finally:
    tasks = []
    for tp in Torpedoes:
        for task in tp.tasks:
            tasks.append({"name": task.name, 
                          "tp": task.tp, 
                          "Finished": task.finished,
                          "Finish Time": task.finishTime})
    
    
    TasksDF = pd.DataFrame(tasks)
    
    infoDF = pd.DataFrame(info)
    infoDF.to_excel(r'Output Locations.xlsx', index = False)
#    generate_GIF2(G, Locomotives, Torpedoes)
    
    
