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
from copy import deepcopy

from PARAMS import H, run_in, suppressOutput
import PARAMS

from ImportNetwork import import_network
from GenerateSnapshot import generate_TPs, generate_Locos, set_TPlocation
from ImportTPdata import generateTaskList, importTpData
from Visualise import generate_GIF2
from ConflictResolution import resolve_conflict

class Simulation:
    def __init__(self, L = 3, pictures = True):
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
        self.Locomotives = generate_Locos(L)

        # KPIs
        self.latePerBaseline = 1
        
        self.latePercentage = None
        self.feasible = True
        self.tasksFinished = 0
        self.LocoIdling = 0
        
    def setBaselines(self):
        print("Setting KPI baselines ...")
        
        # let all locos do nothing.
        Loco_Strat = [('Wait', H+run_in), ('Wait', H+run_in)]
           
        # set to locos
        for i, l in enumerate(self.Locomotives):
            l.strategy = deepcopy(Loco_Strat)
            
        self.run()
        
        self.latePerBaseline = self.latePercentage
        
        self.reset()

    def reset(self):
        for tp in self.Torpedoes:
            tp.reset()
        for l in self.Locomotives:
            l.reset()

        self.latePercentage = None
        self.feasible = True
        self.tasksFinished = 0
        self.LocoIdling = 0

    def run(self, strategy = "strategic", prio = False, keyMomentsPlot = False, gif = False, ExcelOutput = False):

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
        idlingcounter = 0

        try:
            if not suppressOutput:
                print("Simulating")
                
            for t in tqdm(range(1, H + run_in), position=0, leave=True, desc="simulating: "):

#                #testing purposes
#                if t >= 460:
#                    print("stopping point")

                row = {}
                row["t"] = t

                for tp in self.Torpedoes:
                    tp.update(t)
                for l in self.Locomotives:
                    l.update(self.G, self.DiG, t, self.Torpedoes, picking = strategy, prio = prio, storePic = keyMomentsPlot)

                F = self.G.copy()
                DiF = self.DiG.copy()
                for node in [tp.location[t] for tp in self.Torpedoes if tp.Locomotive == None]:
#                    if node == 93:
#                        continue # blijft problemen geven
                    
                    if node in F:
                        F.remove_node(node)
                    if node in DiF:
                        DiF.remove_node(node)

                Loco_pairs = list(combinations(self.Locomotives, 2))
                for pair in Loco_pairs:
#                    print(t, pair[0].name, pair[1].name)
                    resolve_conflict(self.G, self.DiG, F, DiF, pair[0], pair[1], t)

                """ KPIs """
                # lateness at casting node
                CurrentFillTasks = []
                for tp in self.Torpedoes:
                    for task in tp.tasks:
                        if task.name == "Fill" and t > task.EST and t < task.EFT:
                            CurrentFillTasks.append(task)

#                notAtCastingNode = False
                for task in CurrentFillTasks:
                    tp = [i for i in self.Torpedoes if task.tp == i.number][0]
                    if tp.location[t] != task.castingNode:
                        row["TP at castNode"] = False
#                        notAtCastingNode = True
                        latecounter += 1
                    else:
                        row["TP at castNode"] = True
                        
#                latecounter += notAtCastingNode
                        
                # locos idling
                for l in self.Locomotives:
                    if l.state == "Waiting":
                        idlingcounter += 1

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
            self.latePercentage = latecounter / (H+run_in)
            self.LocoIdling = idlingcounter / ((H + run_in) * len(self.Locomotives))
            
            self.tasksFinished = 0
            for tp in self.Torpedoes:
                for t in tp.tasks:
                    self.tasksFinished += int(t.finished)
            
            # print KPI's
            print("Number of timeslots TP too late (both HOO): {} => perc: {:.2%}".format(latecounter, self.latePercentage / self.latePerBaseline if self.latePerBaseline != None else self.latePercentage))
            print("Tasks finished: {}".format(self.tasksFinished))
            print("Mean loco idling time: {:.2%}".format(self.LocoIdling))

            #interpret
            tasks = []
            for tp in self.Torpedoes:
                for task in tp.tasks:
                    tasks.append({"name": task.name,
                                  "tp": task.tp,
                                  "Finished": task.finished,
                                  "Finish Time": task.finishTime,
                                  "Age": task.age})
            if ExcelOutput:
                infoDF = pd.DataFrame(info)
                infoDF.to_excel(r'Output Locations.xlsx', index = False)
                
                TasksDF = pd.DataFrame(tasks)
                TasksDF.to_excel(r'Task states.xlsx', index = False)

            if gif:
                generate_GIF2(self.G, self.Locomotives, self.Torpedoes, dpi=100)

#s = Simulation(L = 2, pictures = False)
#s.reset()
#s.run(strategy = "EDD", prio = False, keyMomentsPlot = False, gif = False, ExcelOutput = True)
#print("simulation run: Feasible={}, LatePercentage={:.2%}, Tasks finished= {}, Mean loco idling time= {:.2%}".format(s.feasible, s.latePercentage, s.tasksFinished, s.LocoIdling))

