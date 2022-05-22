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
from itertools import combinations

from PARAMS import H, run_in

from ImportNetwork import import_network
from GenerateSnapshot import generate_TPs, generate_Locos, set_TPlocation
from ImportTPdata import generateTaskList, importTpData
from Visualise import generate_GIF2
from ConflictResolution import resolve_conflict

class Simulation:
    
    def __init__(self, pictures = True):
        if pictures:
            # clear plot folders:
            files = glob.glob('keyMoments/*.png')
            for f in files:
                os.remove(f)
                
            files = glob.glob('plots/*.png')
            for f in files:
                os.remove(f)
        
        # initialise parameters
        self.DiG = import_network()
        self.G = self.DiG.to_undirected()
        
        self.df = importTpData()
        self.Tasks = generateTaskList(self.G, self.df)
        
        self.Torpedoes = generate_TPs(self.Tasks)
        set_TPlocation(self.DiG, self.df, self.Torpedoes)
        self.Locomotives = generate_Locos(self.DiG)
        
        # KPIs
        self.latePercentage = None
        self.feasible = True
        
    def reset(self):
        for tp in self.Torpedoes:
            tp.reset()
        for l in self.Locomotives:
            l.reset()
            
        self.latePercentage = None
        self.feasible = True

    def run(self, keyMomentsPlot = False, gif = False, ExcelOutput = False):
        
        #interpretation
        info = []
        row = {}
        row["t"] = 0
        for l in self.Locomotives:
            row["loco {} location".format(l.name)] = l.location[0]
        
        for tp in self.Torpedoes:
            row["Tp {} location".format(tp.number)] = tp.location[0]
            row["Tp {} state".format(tp.number)] = tp.state[-1]
                
        info.append(row)
        
        #KPI
        latecounter = 0
        
        try:
            print("Simulating")
            for t in range(1, H+run_in):#tqdm(range(1, H + run_in), position=0, leave=True):
                
#                #testing purposes
#                if t >= 460:
#                    print("stopping point")
                
                row = {}
                row["t"] = t
                
                for tp in self.Torpedoes:
                    tp.update(t)
                for l in self.Locomotives: 
                    l.update(self.G, self.DiG, t, self.Torpedoes, storePic = keyMomentsPlot)
                    
                F = self.G.copy()
                DiF = self.DiG.copy()
                for node in [tp.location[t] for tp in self.Torpedoes if tp.Locomotive == None]:
                    F.remove_node(node)
                    DiF.remove_node(node)
                    
                Loco_pairs = list(combinations(self.Locomotives, 2))
                for pair in Loco_pairs:
#                    print(t, pair[0].name, pair[1].name)
                    resolve_conflict(F, DiF, pair[0], pair[1], t)
                    
                """ KPIs """
                CurrentFillTasks = []
                for tp in self.Torpedoes:
                    for task in tp.tasks:
                        if task.name == "Fill" and t > task.EST and t < task.EFT:
                            CurrentFillTasks.append(task)
                
                for task in CurrentFillTasks:
                    tp = [i for i in self.Torpedoes if task.tp == i.number][0]
                    if tp.location[t] != task.castingNode:
                        row["TP at castNode"] = False
                        latecounter += 1
                    else:
                        row["TP at castNode"] = True
                    
                    
                """ interpretation """
                for l in self.Locomotives:        
                    row["loco {} location".format(l.name)] = l.location[t]
                    row["loco {} state".format(l.name)] = l.state
                    
                for tp in self.Torpedoes:
                    row["Tp {} location".format(tp.number)] = tp.location[t]
                    row["Tp {} state".format(tp.number)] = tp.state[-1]
                    
                info.append(row)
        except Exception:
            self.feasible = False
            traceback.print_exc()
                
        finally:
            # calculate KPI's
            self.latePercentage = latecounter / (2*(H+run_in))
            # print KPI's
            print("Number of timeslots TP too late (both HOO): {} => perc: {:.0%}".format(latecounter, self.latePercentage))
            
            #interpret
            tasks = []
            for tp in self.Torpedoes:
                for task in tp.tasks:
                    tasks.append({"name": task.name, 
                                  "tp": task.tp, 
                                  "Finished": task.finished,
                                  "Finish Time": task.finishTime})    
            
#            TasksDF = pd.DataFrame(tasks)
            
            if ExcelOutput:
                infoDF = pd.DataFrame(info)
                infoDF.to_excel(r'Output Locations.xlsx', index = False)
            
            if gif:
                generate_GIF2(self.G, self.Locomotives, self.Torpedoes, start = 420, end = 480, dpi=100)   
                
                
s = Simulation(pictures = False)

s.run(keyMomentsPlot = False, gif = False, ExcelOutput = False)

print("simulation run: Feasible={}, LatePercentage={}".format(s.feasible, s.latePercentage))
s.reset()
s.run(keyMomentsPlot = False, gif = False, ExcelOutput = False)
print("simulation run: Feasible={}, LatePercentage={}".format(s.feasible, s.latePercentage))

