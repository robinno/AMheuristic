# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:40:18 2022

@author: robin
"""

import pandas as pd
from datetime import datetime, timedelta

from PARAMS import ph, ri

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