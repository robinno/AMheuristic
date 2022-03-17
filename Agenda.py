# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 11:50:56 2022

@author: robin
"""

from Event import Event

class Agenda:
    def __init__(self, horizon):
        self.queue = [Event(horizon, 'end')] # add the list of events
        
    def addEvent(self, event):
        self.queue.append(event) # add event
        self.queue.sort(key=lambda x:x.time) # sort on time
        
    def nextEvent(self):
        event = self.queue.pop(0)
        return event