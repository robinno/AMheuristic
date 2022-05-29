# -*- coding: utf-8 -*-
"""
Created on Thu May 26 16:38:44 2022

@author: robin
"""

import pandas as pd
from datetime import datetime, timedelta

from Simulate import Simulation
import PARAMS

c_strategies = ["EDD", "age", "closest", "minDist", "Hfirst"]

# TODO: halen uit bovenste stuk code
c_timestamps = ['2017-09-27 15:02:40', '2017-09-28 09:02:40', '2017-09-29 12:32:40', '2017-09-30 19:05:23']

c_noLocos = [1]
c_prio = [False, True]


## find valid timestamps:
#t = c_timestamps[-1]
#valids = []
#
##sim = Simulation(L = 2)
#
#while len(valids) < 15:
#    # set starttime
#    currTime = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
#    currTime += timedelta(hours = 5)
#    t = currTime.strftime('%Y-%m-%d %H:%M:%S')
#    
#    valid = True
#    
##    for n in c_noLocos:
##    try:
#    sim = Simulation(startTime = t, L = 2)
#    
#    for s in c_strategies:
#        for p in c_prio:
#            
#            if valid:
#                print("running config: ", t, s, p)
#                
#                try:
#                    sim.run(strategy = s, prio = p)
#                except:
#                    print("problem occured in running simulation")
#                    valid = False
#                
#                if not(sim.feasible):
#                    valid = False
#           
#                sim.reset()
#
#    if valid:
#        valids.append(t)
##    except:
##        pass


# run results.
results = []

for n in c_noLocos:
    for t in c_timestamps:
        sim = Simulation(startTime = t, L = n)
        for s in c_strategies:
            for p in c_prio:
                print("running config: ", n, t, s, p)
                
                sim.run(strategy = s, prio = p)
                
                results.append({"Locos": n,
                                "Strategy": s,
                                "Instance": t,
                                "Prio": p,
                                "Feasible": sim.feasible,
                                "Lateperc": sim.latePercentage,
                                "TaskFinished": sim.tasksFinished,
                                "LocoIdling": sim.LocoIdling})            
                sim.reset()
            
resultDF = pd.DataFrame(results)
resultDF.to_excel(r'Results.xlsx', index = False)    