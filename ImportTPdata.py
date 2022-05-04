# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:40:18 2022

@author: robin
"""

import pandas as pd
import numpy as np
import networkx as nx
from datetime import datetime, timedelta
import math

import Torpedo as torp
import Locomotive as Loco
from Task import Task

from Visualise import plot_Graph2
from ImportNetwork import import_network
from GenerateRoutes import calc_Min_Traveltime

from PARAMS import ph, ri, nD, nRy, nGA, nGB, StartTime, timestep
from PARAMS import connect_slots, D_config_slots
from PARAMS import RyC_config_slots, RyC_init_speed_slots, RyC_speed_slots

def importTpData():

    filepath = r'torpedoData.xlsx'
    
    # convert StartTime
    Start = datetime.strptime(StartTime, '%Y-%m-%d %H:%M:%S')
    
    # import dataframe
    df = pd.read_excel(filepath)
    
    # format the date and time
    df["Tijdstip"] = pd.to_datetime(df["Tijdstip"])
    
# =============================================================================
#   filter the dataframe:
# =============================================================================
    secondsToAdd = ph + ri
    End = Start + timedelta(seconds = secondsToAdd)
    
    df = df[(df['Tijdstip'] > str(Start)) & (df['Tijdstip'] < str(End))]
    
# =============================================================================
#   Clean data
# =============================================================================
    # throw away columns which we wont need:
    del df["CaD"]
    del df["Debiet_CaD"]
    del df["CaD_per_mry"]
    del df["Volume_gas"]
    del df["S_gevr"]
    del df["S_hoo"]
    del df["S_voor"]
    del df["S_her"]
    del df["S_werk"]
    del df["temp_ho"]
    
    # throw away duplicate rows:
    tpLadingen = list(set(df["TPlading"]))
    data = []
    for tpl in tpLadingen:
        row = [row for index, row in df.iterrows() if row["TPlading"] == tpl][0] # get first occurence
        data.append(dict(row))
    
    df = pd.DataFrame(data)
    
    df.reset_index(drop = True) # reset the index
        
    # blaasduur in timeslots
    df["Blaasduur"] = (df["Blaasduur"] / timestep).apply(np.ceil)
    
# =============================================================================
#   add a column on which node is casted:
# =============================================================================
    Cnodes = []
    A_fh = True # first hole
    A_fc = True # first cast
    A_aftap = df[df["Hoo"] == 'A'].iloc[0]["Aftap"]
    
    B_fh = True # first hole
    B_fc = True # first cast
    B_aftap = df[df["Hoo"] == 'B'].iloc[0]["Aftap"]
    
    
    df = df.reset_index()  # make sure indexes pair with number of rows
    for index, row in df.iterrows():
        if row["Hoo"] == 'A':
            if row["Aftap"] != A_aftap:
                A_aftap = row["Aftap"]
                A_fh = True
                A_fc = not(A_fc)               
            
            Cnodes.append(nGA[2*(1-A_fh) + (1-A_fc)])
            
            A_fh = not(A_fh)
            
        else:
            if row["Aftap"] != B_aftap:
                B_aftap = row["Aftap"]
                B_fh = True
                B_fc = not(B_fc)               
            
            Cnodes.append(nGB[2*(1-B_fh) + (1-B_fc)])
            
            B_fh = not(B_fh)
            
    df["Casting Node"] = Cnodes    
    
# =============================================================================
# Add column Tijdstip in time slots:
# =============================================================================
    timeslots = []
    
    for index, row in df.iterrows():
        time_diff = row['Tijdstip'] - Start
        tsecs = time_diff.total_seconds()
        slot = math.floor(tsecs / timestep)
        
        timeslots.append(slot)

    df["Timeslot"] = timeslots
    
    
    df = df.sort_values(by=["Timeslot"])
    del df["index"]
    df = df.reset_index(drop = True)
    
    
# =============================================================================
# Add column Tijdstip of next use
# =============================================================================
    nextUseOfTP_timeslot = []
    
    for index, row in df.iterrows():
        slot = None
        
        #get current tp:
        tp = row["Tp"]
        
        #check if it is used again in the future
        nextuses = [i for i in range(index + 1, len(df)) if df.iloc[i]["Tp"] == tp]
        if(len(nextuses) != 0):
            slot = df["Timeslot"].to_list()[nextuses[0] - 1]
        
        nextUseOfTP_timeslot.append(slot)
        
    df["Next Use Timeslot"] = nextUseOfTP_timeslot
    
# =============================================================================
# Add column for casting time
# =============================================================================
    castingTimes = []
    
    for index, row in df.iterrows():
        beforeDF = df[(df['Timeslot'] < row['Timeslot']) & (df['Hoo'] == row['Hoo'])]
        
        if(len(beforeDF) > 0):
            start = beforeDF.iloc[-1]['Timeslot']
            castingTimes.append(row['Timeslot'] - start)
        else:
            castingTimes.append(None)
        
    df["Casting Time"] = castingTimes
    
# =============================================================================
# Add column for pouring time
# =============================================================================
    pouringTimes = []
    
    for index, row in df.iterrows():
        mry = row["m_ry"] / 1000
        pouringTime = min(30, mry) / RyC_init_speed_slots # first 30 tons
        pouringTime += max(mry - 30, 0) / RyC_speed_slots # rest
        pouringTime = round(pouringTime)
        
        pouringTimes.append(pouringTime)
    
    df["Pouring Time"] = pouringTimes
    
    return df

def estimate_DOF(TasklistDF):
    TasklistDF = TasklistDF[TasklistDF['task'] != "Fill"]
    earliestST = TasklistDF["earliestStartTime"].to_list()
    latestST = TasklistDF["latestStartTime"].to_list()
    
    TotalDOF = 0
    for i in range(len(earliestST)):
        TotalDOF += latestST[i] - earliestST[i]
    return TotalDOF

def generateTaskList(G, df, Torpedoes):    
    
    # make list of tasks
    Tasks = []
    
    for index, row in df.iterrows():
        # fill in the one I know directly: Casting Time!
        Tasks.append({"name": "-> H",
                      "tp": row["Tp"]
                      })
        
        Tasks.append({"name": "Fill",
                      "tp": row["Tp"],
                      "EST": 0 if np.isnan(row["Casting Time"]) else (row["Timeslot"] - row["Casting Time"]),
                      "EFT": row["Timeslot"],
                      "LST": 0 if np.isnan(row["Casting Time"]) else (row["Timeslot"] - row["Casting Time"]),
                      "LFT": row["Timeslot"],
                      "FixedTime": row["Timeslot"] if np.isnan(row["Casting Time"]) else row["Casting Time"],
                      "CastingNode": row["Casting Node"]
                      })
        
        Tasks.append({"name": "-> D",
                      "tp": row["Tp"]
                      })
        
        Tasks.append({"name": "Configure D",
                      "tp": row["Tp"],
                      "FixedTime": D_config_slots
                      })
        
        Tasks.append({"name": "Desulphur",
                      "tp": row["Tp"],
                      "FixedTime": row["Blaasduur"]
                      })
        
        Tasks.append({"name": "-> Ry", 
                      "tp": row["Tp"]
                      })
        
        Tasks.append({"name": "Configure Ry", 
                      "tp": row["Tp"],
                      "FixedTime": RyC_config_slots
                      })
        
        Tasks.append({"name": "Pouring", 
                      "tp": row["Tp"],
                      "FixedTime": row["Pouring Time"]
                      })
        
    Tasks = sorted(Tasks, key = lambda i: i['tp'])
    usedTPs = sorted(list(df.Tp.unique()))
        
    # =============================================================================
    # Cascading Times
    # =============================================================================
    AllTasks = []
    
    for tp in usedTPs:
        currentTPTasks = [i for i in Tasks if i['tp'] == tp]    
        
        # set first EST and EFT => SHOULD BE MOVE TO HOO
        currentTPTasks[0]["EST"] = 0
        currentTPTasks[0]["EFT"] = 0
        
        # forward Cascade
        for i in range(1, len(currentTPTasks)):
            if "EST" not in currentTPTasks[i]:
                currentTPTasks[i]["EST"] = currentTPTasks[i-1]["EFT"]
                
                if "FixedTime" not in currentTPTasks[i]:
                    currentTPTasks[i]["EFT"] = currentTPTasks[i]["EST"]
                else:
                    currentTPTasks[i]["EFT"] = currentTPTasks[i]["EST"] + currentTPTasks[i]["FixedTime"]
                
        
        # backward Cascade
        for i in range(len(currentTPTasks) - 1, 0, -1):
            if "LFT" not in currentTPTasks[i-1] and "LST" in currentTPTasks[i]: # Not none
                currentTPTasks[i-1]["LFT"] = currentTPTasks[i]["LST"]
                
                if "FixedTime" not in currentTPTasks[i-1]:
                    currentTPTasks[i-1]["LST"] = currentTPTasks[i-1]["LFT"]
                else:
                    currentTPTasks[i-1]["LST"] = currentTPTasks[i-1]["LFT"] - currentTPTasks[i-1]["FixedTime"]
        
        # =============================================================================
        # add tasks to Torpedo
        # =============================================================================
        torpedo = [i for i in Torpedoes if i.number == tp][0]
        
        for row in currentTPTasks:
            torpedo.tasks.append(Task(name          = None if "name" not in row else row["name"], 
                                      fixedTime     = None if "FixedTime" not in row else row["FixedTime"],
                                      EST           = None if "EST" not in row else row["EST"], 
                                      LST           = None if "LST" not in row else row["LST"], 
                                      EFT           = None if "EFT" not in row else row["EFT"], 
                                      LFT           = None if "LFT" not in row else row["LFT"],
                                      castingNode   = None if "Casting Node" not in row else row["Casting Node"]
                                      ))
        
        AllTasks += currentTPTasks

    return pd.DataFrame(AllTasks)