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


# cutting the graph
crucial_corners = [14]
exempt_nodes = nG+nD+nRy + crucial_corners