# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 11:11:10 2022

@author: robin
"""


f = open('tsc.msh', 'r')
content = f.read()
content = content.splitlines()
#split on space
for i in range(len(content)):
    content[i] = content[i].split()

# get list of nodes and edges
start = content.index(['$Nodes'])
end = content.index(['$EndNodes'])
nodes = content[start+2:end]

start = content.index(['$Elements'])
end = content.index(['$EndElements'])
edges = content[start+2:end]

#filter self looping edges
fEdges = list(filter(lambda c : c[1] != '15', edges))




