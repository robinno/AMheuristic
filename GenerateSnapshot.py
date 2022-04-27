# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 12:21:43 2022

@author: robin
"""

import Torpedo as torp
import Locomotive as Loco

from Visualise import plot_Graph2
from ImportNetwork import import_network
from ImportTPdata import importTpData

def generate_TPlocations(G):
    
    df = importTpData()

    usedTPs = list(df["Tp"].unique())
    Torpedoes = [torp.Torpedo(i) for i in usedTPs]
    
    # first 5 TPs => 1 under each hole, 3 reserves:
    nodesA = [75,81,127,92,91]
    GietA = df[df["Hoo"] == 'A']
    EersteAftapA = GietA.iloc[0]["Aftap"]
    
    iA = 0
    
    for i in range(5):
        if(GietA.iloc[i]["Aftap"] == EersteAftapA):
            n = GietA.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location = nodesA[i]
            iA = i
        
    
    nodesB = [44,50,105,63,101]
    GietB = df[df["Hoo"] == 'B']
    EersteAftapB = GietB.iloc[0]["Aftap"]
    
    iB = 0
    
    for i in range(5):
        if(GietB.iloc[i]["Aftap"] == EersteAftapB):
            n = GietB.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location = nodesB[i]
            iB = i
            
    # next 2 tps under the other casting hole
    nodesA = [86,90]
    TweedeAftapA = GietA.iloc[iA + 1]["Aftap"]
    
    for i in range(iA+1, iA + 3):
        if(GietA.iloc[i]["Aftap"] == TweedeAftapA):
            n = GietA.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location = nodesA[i - iA - 1]
            
    nodesB = [56,61]
    TweedeAftapB = GietB.iloc[iB + 1]["Aftap"]
    
    for i in range(iB+1, iB + 3):
        if(GietB.iloc[i]["Aftap"] == TweedeAftapB):
            n = GietB.iloc[i]["Tp"]
            torpedo = [x for x in Torpedoes if x.number == n][0]
            torpedo.location = nodesB[i - iB - 1]
            
    # put the other TPs on the straight
    remainingTPs = [tp for tp in Torpedoes if tp.location == None]
    currnode = 171
    
    for tp in remainingTPs:
        tp.location = currnode
        currnode = list(G.successors(currnode))[0]
        
    return Torpedoes
        

G = import_network()
Torpedoes = generate_TPlocations(G)

#Locomotive locations:
Locomotives = [Loco.Locomotive("A", 36),
               Loco.Locomotive("B", 67),
               Loco.Locomotive("C", 21)]


#plot_Graph2(G, [tp for tp in Torpedoes if tp.location != None], [l for l in Locomotives if l.location != None])
plot_Graph2(G, Torpedoes, Locomotives)
