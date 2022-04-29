# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 11:55:00 2022

@author: robin
"""

""" SPECIAL NODES """
nGA = [75,81,90,86]
nGB = [44,50,56,61]
nG = nGA + nGB
nD = [23,27]
nRy = [2,3,10]

# generated in import
nSwitches = []
AccessibleNodes2Ago = []

# global
loco_speed = 10 # in km/h
connection_time = 50 # in seconds
Desulphuring_configuration = 120 + 92 + 92 + 15 # in seconds
RyC_casting_config = 15 + 47 + 30 + 300 + 150 # in seconds
RyC_init_speed = 0.32 # tons / second
RyC_speed = 1.45 # tons / second

# cutting the graph
crucial_corners = [14]
exempt_nodes = nG+nD+nRy + crucial_corners

# conversions
timestep = 3.6 * 20 / loco_speed # tp has length of 20 m
connect_slots = round(connection_time / timestep)
D_config_slots = round(Desulphuring_configuration / timestep)
RyC_config_slots = round(RyC_casting_config / timestep)
RyC_init_speed_slots = RyC_init_speed * timestep # in tons/timeslot
RyC_speed_slots = RyC_speed * timestep # in tons/timeslot

# Planning Horizon in seconds
ph = 24 * 3600
ri = 6  * 3600

H = round(ph / timestep)
#H = 100 # testing
run_in = round(ri / timestep) # number of timesteps run-in

# Globals
T = 0 # number of torpedoes => TESTING
L = 0 # number of locomotives

# where to pick the data
StartTime = '2017-08-26 15:02:40'





