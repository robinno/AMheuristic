# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 12:21:43 2022

@author: robin
"""

import pandas as pd
from datetime import datetime, timedelta

import Torpedo as tp

from PARAMS import ph, ri
from Visualise import plot_Graph2
from ImportNetwork import import_network



def importTpData(StartTime = '2017-08-26 15:03:00'):

    filepath = r'torpedoData.xlsx'
    
    # convert StartTime
    StartTime = datetime.strptime(StartTime, '%Y-%m-%d %H:%M:%S')
    
    # import dataframe
    df = pd.read_excel(filepath)
    
    # throw away columns which we wont need:
    del df["m_ry"]
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
    
    # format the date and time
    df["Tijdstip"] = pd.to_datetime(df["Tijdstip"])
    
    # filter the dataframe:
    secondsToAdd = ph + ri
    EndTime = StartTime + timedelta(seconds = secondsToAdd)
    EndTime = str(EndTime)
    
    df = df[(df['Tijdstip'] > str(StartTime)) & (df['Tijdstip'] < str(EndTime))]
    
    return df

df = importTpData()


usedTPs = list(df["Tp"].unique())
Torpedoes = [tp.Torpedo(i) for i in usedTPs]

# first 5 TPs => 1 under each hole, 3 reserves:
nodesA = [75,81,126,87,86]
GietA = df[df["Hoo"] == 'A']
EersteAftapA = GietA.iloc[0]["Aftap"]

for i in range(5):
    if(GietA.iloc[i]["Aftap"] == EersteAftapA):
        n = GietA.iloc[i]["Tp"]
        torpedo = [x for x in Torpedoes if x.number == n][0]
        torpedo.location = nodesA[i]
    

nodesB = [44,50,56,100,57]
GietB = df[df["Hoo"] == 'B']
EersteAftapB = GietB.iloc[0]["Aftap"]

for i in range(5):
    if(GietB.iloc[i]["Aftap"] == EersteAftapB):
        n = GietB.iloc[i]["Tp"]
        torpedo = [x for x in Torpedoes if x.number == n][0]
        torpedo.location = nodesB[i]
        
plot_Graph2(import_network(), Torpedoes)
