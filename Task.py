# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 17:50:54 2022

@author: robin
"""

from PARAMS import H, run_in

class Task:
    def __init__(self, name, fixedTime = None,
                 starttime = None, endtime = None, 
                 earliestStartTime = 0, latestStartTime = H+run_in-1):
        self.name = name
        self.fixedTime = None if fixedTime == None else int(round(fixedTime))
        self.starttime = None if starttime == None else int(round(starttime))
        self.endtime = None if endtime == None else int(round(endtime))
        self.earliestStartTime = None if earliestStartTime == None else int(round(earliestStartTime))
        self.latestStartTime = None if latestStartTime == None else int(round(latestStartTime))
        