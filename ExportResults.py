# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 09:44:29 2022

@author: robin
"""

import pandas as pd

fLocopos = r"ExcelOutput\Locopos.xlsx"

def output_locopos(LocoPos):
    df = pd.DataFrame(LocoPos)
    
    columns = []
    for l in range(len(LocoPos[0])):
        columns.append("Loco %d"%l)
    
    df.columns = columns
    
    df.to_excel(fLocopos) 
    