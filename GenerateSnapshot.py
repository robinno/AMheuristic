# -*- coding: utf-8 -*-
"""
Created on Tue May  3 20:51:25 2022

@author: robin
"""

import numpy as np

from ImportTPdata import importTpData, generateTaskList
import Torpedo as torp
import Locomotive as Loco
from Task import Task

from Visualise import plot_Graph2
from ImportNetwork import import_network

from PARAMS import nWo, nGA1, nGA2, nGB1, nGB2, nWA1, nWB1


def generate_TPs(Tasks):
    usedTPs = list(Tasks["tp"].unique())
    Torpedoes = [torp.Torpedo(i) for i in usedTPs]
    
    Tasks = Tasks.replace({np.nan: None})
    
    for torpedo in Torpedoes:
        # add tasks to Torpedo
        currentTPTasks = [row for index, row in Tasks.iterrows() if row["tp"] == torpedo.number]  

        for row in currentTPTasks:
            torpedo.tasks.append(Task(name          = None if "name" not in row else row["name"],
                                      tp            = torpedo.number,
                                      fixedTime     = None if "FixedTime" not in row else row["FixedTime"],
                                      EST           = None if "EST" not in row else row["EST"], 
                                      LST           = None if "LST" not in row else row["LST"], 
                                      EFT           = None if "EFT" not in row else row["EFT"], 
                                      LFT           = None if "LFT" not in row else row["LFT"],
                                      castingNode   = None if "CastingNode" not in row else row["CastingNode"]
                                      ))
    
    return Torpedoes

def generate_Locos(DiG):
    #Locomotive locations:
    Locomotives = [Loco.Locomotive("A", 157)]#,
#                   Loco.Locomotive("B", 68)]#,
#                   Loco.Locomotive("C", 147)]
    
    return Locomotives
    
    
def set_TPlocation(G, df, Torpedoes):
    
    # first 5 TPs => 1 under each hole, max 3 reserves:
    nodesA = nGA1 + nWA1
    GietA = df[df["Hoo"] == 'A']
    EersteAftapA = GietA.iloc[0]["Aftap"]
    
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
    
    iA = 0
    
    for i in range(min(5, len(remainingTPs))):
        if(GietA.iloc[i]["Aftap"] == EersteAftapA):
            n = GietA.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location[0] = nodesA[i]
            torpedo.prioMvmt = 1
            iA = i
            
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
        
    
    nodesB = nGB1 + nWB1
    GietB = df[df["Hoo"] == 'B']
    EersteAftapB = GietB.iloc[0]["Aftap"]
    
    iB = 0
    
    for i in range(min(5, len(remainingTPs))):
        if(GietB.iloc[i]["Aftap"] == EersteAftapB):
            n = GietB.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location[0] = nodesB[i]
            torpedo.prioMvmt = 1
            iB = i
            
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
            
    # next 2 tps under the other casting hole
    nodesA = nGA2
    TweedeAftapA = GietA.iloc[iA + 1]["Aftap"]
    
    for i in range(iA+1, iA + 1 + min(2, len(remainingTPs))):
        if(GietA.iloc[i]["Aftap"] == TweedeAftapA):
            n = GietA.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location[0] = nodesA[i - iA - 1]
            
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
            
    nodesB = nGB2
    TweedeAftapB = GietB.iloc[iB + 1]["Aftap"]
    
    for i in range(iB+1, iB + 1 + min(2, len(remainingTPs))):
        if(GietB.iloc[i]["Aftap"] == TweedeAftapB):
            n = GietB.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location[0] = nodesB[i - iB - 1]
            
    # put the other TPs on the straight
    remainingTPs = [tp for tp in Torpedoes if tp.location[0] == None]
    remainingTPs.reverse()
    
    for i in range(len(nWo)):
        if i >= len(remainingTPs):
            break
        
        remainingTPs[i].location[0] = nWo[len(nWo) - i - 1]
        remainingTPs[i].prioMvmt = 2
        
    return Torpedoes

# testing:
#DiG = import_network()
#G = DiG.to_undirected()
#
#df = importTpData()
#Tasks = generateTaskList(G, df)
#
#Torpedoes = generate_TPs(Tasks)
#set_TPlocation(DiG, df, Torpedoes)
#Locomotives = generate_Locos(DiG)
