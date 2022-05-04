# -*- coding: utf-8 -*-
"""
Created on Tue May  3 20:51:25 2022

@author: robin
"""

from ImportTPdata import importTpData
import Torpedo as torp
import Locomotive as Loco


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