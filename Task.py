# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 17:50:54 2022

@author: robin
"""

from params import H

class Task:
    def __init__(self, starttime, endtime, 
                 earliestStartTime = 0, latestEndTime = H):
        self.startTime = starttime
        self.endTime = endtime
        self.earliestStartTime = earliestStartTime
        self.latestEndTime = latestEndTime
        