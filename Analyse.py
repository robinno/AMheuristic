# -*- coding: utf-8 -*-
"""
Created on Thu May 26 16:38:44 2022

@author: robin
"""

import pandas as pd
from datetime import datetime, timedelta

from Simulate import Simulation
import PARAMS

c_strategies = ["EDD", "age", "closest", "minDist"]

# TODO: halen uit bovenste stuk code
c_timestamps = ['2017-09-27 15:02:40']

c_noLocos = [2,3]
c_prio = [True, False]


# find valid timestamps:
PARAMS.StartTime = c_timestamps[-1]

valids = []
maxUnValids = 2

sim = Simulation(L = 2)

while len(valids) < 15:
    # set starttime
    currTime = datetime.strptime(PARAMS.StartTime, '%Y-%m-%d %H:%M:%S')
    currTime += timedelta(hours = 5)
    PARAMS.StartTime = t = currTime.strftime('%Y-%m-%d %H:%M:%S')
    
    unvalids = 0
    
#    for n in c_noLocos:
#        sim = Simulation(L = n)
    for s in c_strategies:
        for p in c_prio:
            
            if unvalids < maxUnValids:
                print("running config: ", t, s, p)
                
                sim.run(strategy = s, prio = p)
                
                if not(sim.feasible):
                    unvalids += 1
           
                sim.reset()

    if unvalids < maxUnValids:
        valids.append(PARAMS.StartTime)


# run results.
#results = []
#
#for n in c_noLocos:
#    sim = Simulation(L = n)
#    for t in c_timestamps:
#        PARAMS.StartTime = t
#        for s in c_strategies:
#            for p in c_prio:
#                print("running config: ", n, t, s, p)
#                
#                sim.run(strategy = s, prio = p)
#                
#                results.append({"Locos": n,
#                                "Strategy": s,
#                                "Instance": t,
#                                "Prio": p,
#                                "Feasible": sim.feasible,
#                                "Lateperc": sim.latePercentage,
#                                "TaskFinished": sim.tasksFinished,
#                                "LocoIdling": sim.LocoIdling})            
#                sim.reset()
#            
#resultDF = pd.DataFrame(results)
#resultDF.to_excel(r'Results.xlsx', index = False)    