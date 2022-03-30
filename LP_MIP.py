# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 13:48:16 2022

@author: robin
"""

import gurobipy as gp
from gurobipy import GRB

from ImportNetwork import import_network 
from Visualise import generate_GIF

#Model definition
m = gp.Model("TP movements")

""" PARAMS """

G = import_network()
N = G.size()

H = 50 # planning horizon

""" VARS """
y = m.addVars(N, H, vtype = GRB.INTEGER, name = "y")


""" OBJECTIVE FUNCTION """
m.setObjective(1, GRB.MINIMIZE)


""" CONSTRAINTS """
# Locomotive located somewhere
m.addConstrs(sum(y[n,t] for n in list(G.nodes())) == 1 
                for t in range(H)
            )

# Neighbors are 1 => ROUTING
m.addConstrs(y[n,t-1] + sum(y[k,t-1] for k in list(G.neighbors(n))) >= y[n,t] 
                for n in list(G.nodes()) 
                for t in range(1, H)
            )



# INIT TEST
# Loco start at 5
m.addConstr(y[5,0] == 1)
# Loco start at 5
m.addConstr(y[95,H-1] == 1)

""" RUN THE MODEL """
m.optimize()

""" INTERPRET RESULTS """

# interpret y variables
loco_pos = []
for t in range(H):
    for n in list(G.nodes()):
        if y[n,t].x == 1:
            loco_pos.append(n)
            
# generate gif
generate_GIF(G, H, loco_pos)