# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 13:48:16 2022

@author: robin
"""

import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import networkx as nx

from ImportNetwork import import_network 
from Visualise import generate_GIF

from PARAMS import nSwitches, nG, nD, nRy, L, T, H

# helper function
def edgeIndex(G, edge):    
    return list(G.edges()).index(edge)

#Model definition
m = gp.Model("TP movements")

""" TUNING """

m.params.MIPFocus = 1 # focus on finding feasible solutions
m.params.Presolve = 2 # aggressive presolve

""" PARAMS """
M = 1000 # big M

G = import_network()

##########################
#### TEST: small network
#G = nx.DiGraph()
#for n in range(6+1):
#    G.add_node(n, pos =(float(n),float(n)))
#    if not(n==0):
#        G.add_edge(n-1,n)

#pos=nx.get_node_attributes(G,'pos')
#nx.draw(G, pos, with_labels = True)
###############################

N = len(G.nodes())
E = len(G.edges())

""" VARS """
y = m.addVars(N, L, H, vtype = GRB.BINARY, name = "y")  # loco location
ld = m.addVars(L, H, vtype = GRB.BINARY, name = "ld")   # loco direction

x = m.addVars(N, T, H, vtype = GRB.BINARY, name = "x")  # tp location

Nf = m.addVars(E, L, T, H, vtype = GRB.BINARY, name = "Nf")    # Neighbors front
cf = m.addVars(L, T, H, vtype = GRB.BINARY, name = "cf")       # connection front

Nb = m.addVars(E, L, T, H, vtype = GRB.BINARY, name = "Nb")    # Neighbors back
cb = m.addVars(L, T, H, vtype = GRB.BINARY, name = "cb")       # connection back

tm = m.addVars(T, H, vtype = GRB.BINARY, name = "tm")   #torpedo is allowed to move (moveable)


""" OBJECTIVE FUNCTION """
m.setObjective(1, GRB.MINIMIZE)
#m.setObjective(sum(cf[l,j,t] for l in range(L) for j in range(T) for t in range(H)),
#               GRB.MAXIMIZE
#               )

""" CONSTRAINTS """

# =============================================================================
# LOCO CONSTRAINTS
# =============================================================================

# Locomotive located somewhere
m.addConstrs(sum(y[n, l, t] for n in G.nodes()) == 1 
                for l in range(L)
                for t in range(H)
            )

# Locomotive NOT on special node
m.addConstrs(y[n,l,t] == 0 
             for n in nG + nD
             for l in range(L)
             for t in range(H))

# Neighbors are 1 => ROUTING
# Mutually exclusive contraints
m.addConstrs(y[n, l, t] + sum(y[k, l, t] for k in list(G.successors(n))) >= y[n,l,t+1] - M * (1 - ld[l, t+1])
                for n in G.nodes()
                for t in range(H - 1)
                for l in range(L)
            )

m.addConstrs(y[n, l, t] + sum(y[k, l, t] for k in list(G.predecessors(n))) >= y[n,l,t+1] - M * (ld[l, t+1])
                for n in G.nodes()
                for t in range(H - 1)
                for l in range(L)
            )

# Sharp corners => no direction change on switch
# Split up equality constraint from IF !!!
m.addConstrs(ld[l,t] - ld[l,t + 1] <= M * (1 - y[n,l,t]) 
                for n in nSwitches
                for l in range(L)
                for t in range(H-1)
            )

m.addConstrs(ld[l,t] - ld[l,t + 1] >= - M * (1 - y[n,l,t]) 
                for n in nSwitches
                for l in range(L)
                for t in range(H-1)
            )

# TORPEDOs ADDED HERE
# max 1 vehicle per node
m.addConstrs(sum(y[n, l, t] for l in range(L)) + sum(x[n, i, t] for i in range(T)) <= 1
                 for n in G.nodes()
                 for t in range(H)
            )

# No crossing
# n = from node
# k = to node
m.addConstrs(y[n,l,t] + y[k,j,t] + y[n,j,t+1] + y[k,l,t+1] <= 3 
                for (n,k) in G.edges()
                for l in range(L)
                for j in range(L)
                for t in range(H-1)
            )

# No crossing loco - tp as well
# n = from node
# k = to node
m.addConstrs(y[n,l,t] + x[k,j,t] + x[n,j,t+1] + y[k,l,t+1] <= 3 
                for (n,k) in G.edges()
                for l in range(L)
                for j in range(T)
                for t in range(H-1)
            )

m.addConstrs(y[k,l,t] + x[n,j,t] + x[k,j,t+1] + y[n,l,t+1] <= 3 
                for (n,k) in G.edges()
                for l in range(L)
                for j in range(T)
                for t in range(H-1)
            )

# =============================================================================
# TORPEDO CONSTRAINTS
# =============================================================================

# tp located somewhere
m.addConstrs(sum(x[n, i, t] for n in G.nodes()) == 1
                for i in range(T)
                for t in range(H-1)
            )

# tp routing
m.addConstrs(x[n, l, t] + sum(x[k, l, t] for k in list(G.successors(n)) + list(G.predecessors(n))) >= x[n,l,t+1]
                for n in G.nodes()
                for t in range(H - 1)
                for l in range(L)
            )

# set the tp moveable flag: is it connected?
m.addConstrs(2 * tm[i,t] <= sum(cf[l,i,t] + cf[l,i,t+1] + cb[l,i,t] + cb[l,i,t+1] for l in range(L))
                for i in range(T)
                for t in range(H-1))


# SPLIT UP CONSTRAINT:
# only move the TP if its moveable
m.addConstrs(x[n,i,t] - x[n,i,t+1] <= M * tm[i,t]
                for n in G.nodes()
                for i in range(T)
                for t in range(H-1))

m.addConstrs(x[n,i,t] - x[n,i,t+1] >= - M * tm[i,t]
                for n in G.nodes()
                for i in range(T)
                for t in range(H-1))

# =============================================================================
# CONNECTIONS
# =============================================================================

# loco can only push/pull, not simultaneously
m.addConstrs(sum(cf[l,i,t] + cb[l,i,t] for i in range(T)) <= 1
                 for l in range(L)
                 for t in range(H))


# Neighbors flag
m.addConstrs(2 * Nf[edgeIndex(G, (n,k)), l, i, t] <= y[k,l,t] + x[n,i,t]
                for (n,k) in G.edges()
                for l in range(L)
                for i in range(T)
                for t in range(H)
            )

m.addConstrs(2 * Nb[edgeIndex(G, (n,k)), l, i, t] <= y[n,l,t] + x[k,i,t]
                for (n,k) in G.edges()
                for l in range(L)
                for i in range(T)
                for t in range(H)
            )

# Connection only allowed if neighbors
m.addConstrs(cf[l,i,t] <= sum(Nf[edgeIndex(G, (n,k)),l,i,t] for (n,k) in G.edges())
                for l in range(L)
                for i in range(T)
                for t in range(H)
            )

m.addConstrs(cb[l,i,t] <= sum(Nb[edgeIndex(G, (n,k)),l,i,t] for (n,k) in G.edges())
                for l in range(L)
                for i in range(T)
                for t in range(H)
            )

pass

# INIT TEST
#m.addConstr(y[115,0,0] == 1)
#m.addConstr(y[120,0,H-1] == 1)

#m.addConstr(cMf[0,0,H-1] == 1)

#m.addConstr(y[120,1,0] == 1)
#m.addConstr(y[115,1,H-1] == 1)
#
#m.addConstr(y[100,2,0] == 1)
#m.addConstr(y[15,2,H-1] == 1)

#m.addConstr(x[118,0,30] == 1)

#m.addConstr(cMf[0,0,4] == 1)

#m.addConstr(y[116,0,2] == 1)
#m.addConstr(x[115,0,2] == 1)
#
#m.addConstr(y[115,0,4] == 1)
#m.addConstr(x[116,0,4] == 1)

#m.addConstr(y[1,0,2] == 1)
#m.addConstr(x[2,0,2] == 1)
#
m.addConstr(y[69,0,0] == 1)
m.addConstr(x[44,0,0] == 1)

m.addConstr(y[69,0,H-3] == 1)
m.addConstr(x[27,0,H-3] == 1)


""" RUN THE MODEL """
m.optimize()

#troubleshooting
m.write('model troubleshooting.lp')
m.write('model troubleshooting.mps')

""" INTERPRET RESULTS """

Locations = []
for t in range(H):
    Location = {}
    
    # LOCO interpretation
    for l in range(L):
        
        # direction 
#        Location["Loco %d dir"%l] = ld[l,t].x
        
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
                
    # Connection interpretation
    for l in range(L):
        connectedTP = -1
        
        for j in range(T):
            if cf[l,j,t].x == 1:
                connectedTP = j
        
        Location["Loco %d front connection to TP"%l] = connectedTP
        
        connectedTP = -1
        
        for j in range(T):
            if cb[l,j,t].x == 1:
                connectedTP = j
        
        Location["Loco %d back connection to TP"%l] = connectedTP
        
    # torpedo moveable
    for i in range(T):
        Location["TP %d moveable flag"%i] = (tm[i,t].x == 1)
    
    
    # append per timeslot
    Locations.append(Location)

# =============================================================================
# OUTPUT EXCEL
# =============================================================================
print("output to excel")
df = pd.DataFrame(Locations)    
df.to_excel(r"ExcelOutput\Positions.xlsx") 

# generate gif
generate_GIF(G, Locations)

print("Done!")


    
