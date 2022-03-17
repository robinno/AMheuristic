# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 11:52:56 2022

@author: robin
"""

class Event:
    
    def __init__(self, time, kind):
        self.time = time
        self.kind = kind
    
    def __str__(self):
        return self.kind