# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 17:48:46 2022

@author: robin
"""
import numpy as np
from random import choices

from PARAMS import stratLength

# GA params
popSize = 100

# probability picking wrt waiting
prob_pick = 0.5

# picking number and waiting time will be geometric distributions
p_pick = 0.5
p_wait = 0.1

def gen_Pick():
    x = np.random.geometric(p_pick) - 1
    
    return ("Pick", x)
    
def gen_Wait():
    x = np.random.geometric(p_wait) - 1
    
    return ("Wait", x)

def gen_Genome():
    action = choices(
                population =    ["Pick" , "Wait"], 
                weights =       [prob_pick  , 1-prob_pick],
                k =             stratLength
            )
    
    genome = []
    
    for i in action:
        if i == "Pick":
            genome.append(gen_Pick())
        else:
            genome.append(gen_Wait())
    
    return genome

def gen_Population():
    return [gen_Genome() for _ in range(popSize)]

population = gen_Population()