# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 11:55:00 2022

@author: robin
"""

""" SPECIAL NODES """

#Casting holes:
nGA1 = [75,81]
nGA2 = [90,86]
nGA = nGA1+nGA2

nGB1 = [44,50]
nGB2 = [56,61]
nGB = nGB1+nGB2

nG = nGA + nGB

#Waiting nodes:
nWA1 = [127,92,91]
nFA1 = [126]
nWA2 = [125, 124, 82]
nFA2 = [130]

nWB1 = [105,63,101]
nFB1 = [104]
nWB2 = [103, 51, 99]
nFB2 = [102]

nWo = [39, 168, 167, 166, 165, 164]

#Desulphuring nodes
nD = [23,27]

#Emptying nodes
nRy = [2,3,10]

# generated in import
nSwitches = []
AccessibleNodes2Ago = []

# cutting the graph
crucial_corners = [14]
exempt_nodes = nG+nD+nRy + crucial_corners

""" GLOBALS """
loco_speed = 10 # in km/h
connection_time = 50 # in seconds
Allowed_Connections = 3 # TPs in front or at back of loco allowed
Desulphuring_configuration = 120 + 92 + 92 + 15 # in seconds
RyC_casting_config = 15 + 47 + 30 + 300 + 150 # in seconds
RyC_init_speed = 0.32 # tons / second
RyC_speed = 1.45 # tons / second

# conversions
timestep = 3.6 * 20 / loco_speed # tp has length of 20 m
connect_slots = round(connection_time / timestep)
D_config_slots = round(Desulphuring_configuration / timestep)
RyC_config_slots = round(RyC_casting_config / timestep)
RyC_init_speed_slots = RyC_init_speed * timestep # in tons/timeslot
RyC_speed_slots = RyC_speed * timestep # in tons/timeslot

# Planning Horizon in seconds
ph = 12 * 3600
ri = 0  * 3600

H = round(ph / timestep)
#H = 100 # testing
run_in = round(ri / timestep) # number of timesteps run-in

# Globals for MIP
T = 0 # number of torpedoes => TESTING
L = 0 # number of locomotives

# where to pick the data
StartTime = '2017-08-27 15:02:40'





