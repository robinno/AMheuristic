# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 11:48:56 2022

@author: robin
"""

from Event import Event
from Agenda import Agenda

class DES:
    def __init__(self, horizon):
        # BASIC ELEMENTS
        self.now = 0 # current time
        self.agenda = Agenda(horizon)
        
        # FOR ANALYSIS
        self.count = 0 # number of events triggered
        
    def add_event(self, dt, kind):
        event = Event(self.now + dt, kind)
        self.agenda.append(event)
        
    """ EVENTS """
    # TODO
    
    """ OUTPUT """
    def print_state(self):
        print("{} th event occurs at time {}".format(self.count, round(self.now)))

    """ RUN """
    def run(self):
        while True:
            self.print_state()
            event = self.agenda.nextEvent()
            print(event)
            
            self.now = event.time # advance the simulation time
            self.count += 1
            
            # END CASE
            if event.kind == 'end':
                print("Ending event; terminating simulation")
                break
            
            # RUN THE EVENT
            # TODO
          
d = DES(100)
d.run()
    
    
        