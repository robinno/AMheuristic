# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 09:44:29 2022

@author: robin
"""

import pandas as pd

fLocopos = r"ExcelOutput\Locopos.xlsx"

def output_locopos(LocoPos, loco_dir):
    df = pd.DataFrame(LocoPos)
    
    columns = []
    for l in range(len(LocoPos[0])):
        columns.append("Loco %d"%l)
    
    df.columns = columns
    
    for l in range(len(loco_dir)):
        df["Loco %d direction"%l] = loco_dir[l]
    
    df.to_excel(fLocopos) 
    