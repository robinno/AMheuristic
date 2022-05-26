# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 17:50:54 2022

@author: robin
"""

from PARAMS import H, run_in

class Task:
    def __init__(self, name, tp, fixedTime = None,
                 EST = 0, LST = H+run_in-1,
                 EFT = 0, LFT = H+run_in-1,
                 castingNode = None):
        self.name = name
        self.tp = tp
        self.fixedTime = None if fixedTime == None else int(round(fixedTime))
        
        self.EST = None if EST == None else int(round(EST))
        self.LST = None if LST == None else int(round(LST))
        self.EFT = None if EFT == None else int(round(EFT))
        self.LFT = None if LFT == None else int(round(LFT))
        
        self.castingNode = castingNode
        self.finished = False
        self.finishTime = None
        
        self.age = 0
        