# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 13:48:16 2022

@author: robin
"""

import gurobipy as gp
from gurobipy import GRB

from ImportNetwork import import_network 
from Visualise import generate_GIF
from ExportResults import output_locopos

from PARAMS import nSwitches

#Model definition
m = gp.Model("TP movements")

""" PARAMS """

M = 1000000 # big M

G = import_network()
N = G.size()

L = 1 # number of locomotives

H = 50 # planning horizon

""" VARS """
y = m.addVars(N, L, H, vtype = GRB.BINARY, name = "y")
ld = m.addVars(L, H, vtype = GRB.BINARY, name = "ld") # locomotive direction


""" OBJECTIVE FUNCTION """
m.setObjective(1, GRB.MINIMIZE)


""" CONSTRAINTS """
# Locomotive located somewhere
m.addConstrs(sum(y[n, l, t] for n in list(G.nodes())) == 1 
                for l in range(L)
                for t in range(H)
            )

# Neighbors are 1 => ROUTING
# Mutually exclusive contraints
m.addConstrs(y[n, l, t-1] + sum(y[k, l, t-1] for k in list(G.successors(n))) >= y[n,l,t] - M * (1 - ld[l, t])
                for n in list(G.nodes())
                for t in range(1, H)
                for l in range(L)
            )

m.addConstrs(y[n, l, t-1] + sum(y[k, l, t-1] for k in list(G.predecessors(n))) >= y[n,l,t] - M * (ld[l, t])
                for n in list(G.nodes())
                for t in range(1, H)
                for l in range(L)
            )

# Sharp corners => no direction change on switch
# Split up equality constraint from IF !!!
m.addConstrs(ld[l,t] - ld[l,t + 1] <= M * (1 - y[n,l,t]) 
                for n in nSwitches
                for l in range(L)
                for t in range(H-1))

m.addConstrs(ld[l,t] - ld[l,t + 1] >= - M * (1 - y[n,l,t]) 
                for n in nSwitches
                for l in range(L)
                for t in range(H-1))


pass

# INIT TEST
m.addConstr(y[5,0,0] == 1)
m.addConstr(y[95,0,H-1] == 1)

#m.addConstr(y[110,1,0] == 1)
#m.addConstr(y[20,1,H-1] == 1)
#
#m.addConstr(y[100,2,0] == 1)
#m.addConstr(y[15,2,H-1] == 1)

""" RUN THE MODEL """
m.optimize()

""" INTERPRET RESULTS """

# interpret y variables
loco_pos = []
for t in range(H):
    lpos = []
    for n in list(G.nodes()):
        for l in range(L):
            if y[n,l,t].x == 1:
                lpos.append(n)
    loco_pos.append(lpos)
    
# interpret ld variables
loco_dir = []
for l in range(L):
    ldir = []
    for t in range(H):
        ldir.append(ld[l,t].x)
    loco_dir.append(ldir)
            
# generate gif
generate_GIF(G, H, loco_pos)
output_locopos(loco_pos, loco_dir)


    
