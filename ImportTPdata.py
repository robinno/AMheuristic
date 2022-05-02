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
    return df

def generate_TPlocations(G):
    
    df = importTpData()

    usedTPs = list(df["Tp"].unique())
    Torpedoes = [torp.Torpedo(i) for i in usedTPs]
    
    # first 5 TPs => 1 under each hole, 3 reserves:
    nodesA = [75,81,127,92,91]
    GietA = df[df["Hoo"] == 'A']
    EersteAftapA = GietA.iloc[0]["Aftap"]
    
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
    
    iA = 0
    
    for i in range(min(5, len(remainingTPs))):
        if(GietA.iloc[i]["Aftap"] == EersteAftapA):
            n = GietA.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location[0] = nodesA[i]
            iA = i
            
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
        
    
    nodesB = [44,50,105,63,101]
    GietB = df[df["Hoo"] == 'B']
    EersteAftapB = GietB.iloc[0]["Aftap"]
    
    iB = 0
    
    for i in range(min(5, len(remainingTPs))):
        if(GietB.iloc[i]["Aftap"] == EersteAftapB):
            n = GietB.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location[0] = nodesB[i]
            iB = i
            
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
            
    # next 2 tps under the other casting hole
    nodesA = [86,90]
    TweedeAftapA = GietA.iloc[iA + 1]["Aftap"]
    
    for i in range(iA+1, iA + 1 + min(2, len(remainingTPs))):
        if(GietA.iloc[i]["Aftap"] == TweedeAftapA):
            n = GietA.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location[0] = nodesA[i - iA - 1]
            
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
            
    nodesB = [56,61]
    TweedeAftapB = GietB.iloc[iB + 1]["Aftap"]
    
    for i in range(iB+1, iB + 1 + min(2, len(remainingTPs))):
        if(GietB.iloc[i]["Aftap"] == TweedeAftapB):
            n = GietB.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location[0] = nodesB[i - iB - 1]
            
    # put the other TPs on the straight
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
    currnode = 171
    
    for tp in remainingTPs:
        tp.location[0] = currnode
        currnode = list(G.successors(currnode))[0]
        
    return Torpedoes

def generate_Locolocations(G):
    #Locomotive locations:
    Locomotives = [Loco.Locomotive("A", 36)]#,
#                   Loco.Locomotive("B", 67),
#                   Loco.Locomotive("C", 21)]
    
    return Locomotives


def AddTasksToTp(G, Torpedoes, gietLijst):
    
    # =============================================================================
    #  cycle for each TP:
    #  move to HOO -> full -> move to DP -> desulphur -> move to RyC -> empty -> move to HOO
    # =============================================================================
    
    # IMPORTANT!! ASSUMES ALL TPs are EMPTY
    # otherwise: code should be added   
    
    gietLijst = gietLijst.reset_index(drop = True)
    minTravelTimes = calc_Min_Traveltime(G)

    for index, row in gietLijst.iterrows():    
        # get current line information
        tp = row["Tp"]
        torpedo = [x for x in Torpedoes if x.number == tp][0]
        startTime = row["Timeslot"]
        
        # when is torpedo used next at HOO?
        tplist = gietLijst["Tp"].to_list()
        
        nextuses = [i for i in range(index + 1, len(gietLijst)) if tplist[i] == tp]
        
        if(len(nextuses)==0):
            continue
        
        nextuseIndex = nextuses[0]
        endTime = gietLijst["Timeslot"].to_list()[nextuseIndex - 1]
        nextCastingNode =  gietLijst["Casting Node"].to_list()[nextuseIndex]
        
        nextFillTimeStart = gietLijst["Timeslot"].to_list()[nextuseIndex - 1]
        nextFillTimeEnd = gietLijst["Timeslot"].to_list()[nextuseIndex]
        
        # timing information
        node = row["Casting Node"]
        minTimeGAD = min(minTravelTimes[(node, i)] for i in nD)
        
        blaasDuur = row["Blaasduur"]
        
        minTimeDRy = min(minTravelTimes[(i,j)] for i in nD for j in nRy)
        
        mry = row["m_ry"] / 1000
        pouringTime = min(30, mry) / RyC_init_speed_slots # first 30 tons
        pouringTime += max(mry - 30, 0) / RyC_speed_slots # rest
        pouringTime = round(pouringTime)
        
        minTimeRyG = min(minTravelTimes[(i, nextCastingNode)] for i in nRy)
        
        # set endTime correctly:
        endTime -= connect_slots + minTimeGAD 
        endTime -= connect_slots + D_config_slots + blaasDuur
        endTime -= connect_slots + minTimeDRy 
        endTime -= connect_slots + RyC_config_slots + pouringTime 
        endTime -= connect_slots + minTimeRyG
        endTime -= connect_slots 
        
        # Connect
        torpedo.tasks.append(Task("Connect", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime,
                                  fixedTime = connect_slots))
        startTime += connect_slots
        endTime += connect_slots
        
        # move to Desulphurisation plant
        torpedo.tasks.append(Task("G -> D", 
                                  earliestStartTime = startTime,
                                  latestStartTime = endTime))
        startTime += minTimeGAD
        endTime += minTimeGAD
        
        # Disconnect
        torpedo.tasks.append(Task("Disconnect", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = connect_slots))
        startTime += connect_slots
        endTime += connect_slots
        
        # Add the desulphurisation configuration time
        torpedo.tasks.append(Task("Configure Desulphur", 
                                  earliestStartTime = startTime,
                                  latestStartTime = endTime, 
                                  fixedTime = D_config_slots))
        startTime += D_config_slots
        endTime += D_config_slots
        
        # Desulphur
        torpedo.tasks.append(Task("Desulphur", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = blaasDuur))
        startTime += blaasDuur
        endTime += blaasDuur 
        
        # Connect
        torpedo.tasks.append(Task("Connect", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = connect_slots))
        startTime += connect_slots
        endTime += connect_slots 
        
        # move to RyC
        torpedo.tasks.append(Task("D -> Ry", 
                                  earliestStartTime = startTime,
                                  latestStartTime = endTime))
        startTime += minTimeDRy
        endTime += minTimeDRy 
        
        # Disconnect
        torpedo.tasks.append(Task("Disconnect", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = connect_slots))
        startTime += connect_slots
        endTime += connect_slots 
        
        # configure casting
        torpedo.tasks.append(Task("Configure RyC", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = RyC_config_slots))
        startTime += RyC_config_slots
        endTime += RyC_config_slots 
        
        # pouring at RyC
        torpedo.tasks.append(Task("Pouring RyC", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = pouringTime))
        startTime += pouringTime
        endTime += pouringTime 
        
        # Connect
        torpedo.tasks.append(Task("Connect", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = connect_slots))
        startTime += connect_slots
        endTime += connect_slots 
        
        # Move to HOO
        torpedo.tasks.append(Task("Ry -> G", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = connect_slots))
        startTime += minTimeRyG
        endTime += minTimeRyG
        
        # Disconnect
        torpedo.tasks.append(Task("Disconnect", 
                                  earliestStartTime = startTime, 
                                  latestStartTime = endTime, 
                                  fixedTime = connect_slots))
        startTime += connect_slots
        endTime += connect_slots 
        
        # Fill at HOO
        torpedo.tasks.append(Task("Fill",
                                  starttime = nextFillTimeStart,
                                  endtime = nextFillTimeEnd,
                                  fixedTime = nextFillTimeEnd - nextFillTimeStart))
         
def generateTaskList(G, df, Torpedoes):
    GietA = df[df["Hoo"] == 'A'].reset_index(drop = True)
    GietB = df[df["Hoo"] == 'B'].reset_index(drop = True)
    
    AddTasksToTp(G, Torpedoes, GietA)
    AddTasksToTp(G, Torpedoes, GietB)
    
    # full task list:
    Tasklist = []
    for tp in Torpedoes:
        for task in tp.tasks:
            Tasklist.append({"tp": tp.number, "task": task.name, "fixedTime": task.fixedTime, 
                             "starttime": task.starttime,"endtime": task.endtime, 
                             "earliestStartTime": task.earliestStartTime, 
                             "latestStartTime": task.latestStartTime})
    
    TasklistDF = pd.DataFrame(Tasklist)
    
    return TasklistDF.sort_values(["earliestStartTime"])
        
def estimate_DOF(TasklistDF):
    TasklistDF = TasklistDF[TasklistDF['task'] != "Fill"]
    earliestST = TasklistDF["earliestStartTime"].to_list()
    latestST = TasklistDF["latestStartTime"].to_list()
    
    TotalDOF = 0
    for i in range(len(earliestST)):
        TotalDOF += latestST[i] - earliestST[i]
    return TotalDOF
    
#G = import_network()
#Torpedoes = generate_TPlocations(G)
#Locomotives = generate_Locolocations(G)
#
#plot_Graph2(G, [tp for tp in Torpedoes if tp.location != None], [l for l in Locomotives if l.location != None])
#plot_Graph2(G, 0, Torpedoes, Locomotives)
#    
#df = importTpData()
#G = import_network()
#Torpedoes = generate_TPlocations(G)
#
#generateTaskList(G, df, Torpedoes)
