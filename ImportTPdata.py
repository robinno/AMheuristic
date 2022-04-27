# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:40:18 2022

@author: robin
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from PARAMS import ph, ri, nGA, nGB, StartTime, timestep

def importTpData():

    filepath = r'torpedoData.xlsx'
    
    # convert StartTime
    Start = datetime.strptime(StartTime, '%Y-%m-%d %H:%M:%S')
    
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
    
    # blaasduur in timeslots
    df["Blaasduur"] = (df["Blaasduur"] / timestep).apply(np.ceil)
    
# =============================================================================
#   filter the dataframe:
# =============================================================================
    secondsToAdd = ph + ri
    End = Start + timedelta(seconds = secondsToAdd)
    
    df = df[(df['Tijdstip'] > str(Start)) & (df['Tijdstip'] < str(End))]
    
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
    
    return df

#
#def generateTaskList():

df = importTpData()
# first TP is in location