# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 13:48:16 2022

@author: robin
"""

import gurobipy as gp
from gurobipy import GRB
import pandas as pd

from ImportNetwork import import_network 
from Visualise import generate_GIF

from PARAMS import nSwitches, nG, nD, nRy, L, T, H

#Model definition
m = gp.Model("TP movements")

""" PARAMS """

M = 1000000 # big M

G = import_network()
N = G.size()

""" VARS """
y = m.addVars(N, L, H, vtype = GRB.BINARY, name = "y")  # loco location
ld = m.addVars(L, H, vtype = GRB.BINARY, name = "ld")   # loco direction

x = m.addVars(N, T, H, vtype = GRB.BINARY, name = "x")  # tp location


""" OBJECTIVE FUNCTION """
m.setObjective(1, GRB.MINIMIZE)


""" CONSTRAINTS """

# =============================================================================
# LOCO CONSTRAINTS
# =============================================================================

# Locomotive located somewhere
m.addConstrs(sum(y[n, l, t] for n in list(G.nodes())) == 1 
                for l in range(L)
                for t in range(H)
            )

# Locomotive NOT on special node
m.addConstrs(y[n,l,t] == 0 
             for n in nG + nD + nRy
             for l in range(L)
             for t in range(H))

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

# TORPEDOs ADDED HERE
# max 1 vehicle per node
m.addConstrs(sum(y[n, l, t] for l in range(L)) + sum(x[n, i, t] for i in range(T)) <= 1
                 for n in G.nodes()
                 for t in range(H))

# No crossing
# n = from node
# k = to node
m.addConstrs(y[n,l,t] + y[k,j,t] + y[n,j,t+1] + y[k,l,t+1] <= 3 
                for (n,k) in list(G.edges())
                for l in range(L)
                for j in range(L)
                for t in range(H-1))

# =============================================================================
# TORPEDO CONSTRAINTS
# =============================================================================

# tp located somewhere
m.addConstrs(sum(x[n, i, t] for n in list(G.nodes())) == 1 
                for i in range(T)
                for t in range(H)
            )

pass

# INIT TEST
m.addConstr(y[115,0,0] == 1)
m.addConstr(y[120,0,H-1] == 1)

m.addConstr(y[120,1,0] == 1)
m.addConstr(y[115,1,H-1] == 1)
#
#m.addConstr(y[100,2,0] == 1)
#m.addConstr(y[15,2,H-1] == 1)

""" RUN THE MODEL """
m.optimize()

""" INTERPRET RESULTS """

Locations = []
for t in range(H):
    Location = {}
    
    # LOCO interpretation
    for l in range(L):
        
        # direction 
        Location["Loco %d dir"%l] = ld[l,t].x
        
        # position 
        for n in list(G.nodes()):
            if y[n,l,t].x == 1:
                Location["Loco %d pos"%l] = n        
                
    # TP interpretation
    for i in range(T):
        # position 
        for n in list(G.nodes()):
            if x[n,i,t].x == 1:
                Location["TP %d pos"%i] = n  
    
    Locations.append(Location)
    
# generate gif
generate_GIF(G, Locations)


# =============================================================================
# OUTPUT EXCEL
# =============================================================================
df = pd.DataFrame(Locations)    
df.to_excel(r"ExcelOutput\Positions.xlsx") 

print("Done!")


    
