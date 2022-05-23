# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 17:48:46 2022

@author: robin
"""
import numpy as np
from random import choices, randint, random
from itertools import groupby
from tqdm import tqdm
from copy import deepcopy

from PARAMS import stratLength, suppressOutput
from Simulate import Simulation

# GA params
popSize = 10
mutProb = 0.1
generations = 10

# probability picking or waiting
prob_pick = 0.5

# picking number and waiting time will be geometric distributions
p_pick = 0.7
p_wait = 0.02

def gen_Pick():
    x = np.random.geometric(p_pick) - 1
    
    return ("Pick", x)
    
def gen_Wait():
    x = np.random.geometric(p_wait) - 1
    
    return ("Wait", x)

def gen_Genome(no_locos):
    genome = []
    
    for _ in range(no_locos):
        action = choices(
                    population =    ["Pick" , "Wait"], 
                    weights =       [prob_pick  , 1-prob_pick],
                    k =             stratLength
                )
        
        for i in action:
            if i == "Pick":
                genome.append(gen_Pick())
            else:
                genome.append(gen_Wait())
                
        genome.append(None)
        
    genome[:-1]
    
    return genome

def gen_Population(no_locos):
    return [gen_Genome(no_locos) for _ in range(popSize)]

def fitness(s, genome, save=False):
   s.reset()
      
   # split genome:
   Loco_Strat = [list(group) for k, group in groupby(genome, lambda x: x == None) if not k]
   
   # set to locos
   for i, l in enumerate(s.Locomotives):
       l.strategy = Loco_Strat[i]
   
   s.run(keyMomentsPlot = save, gif = save, ExcelOutput = save)
   
   # extract KPIs
   feasible = s.feasible
   latePercentage = s.latePercentage
   
   return latePercentage if feasible else 10 # penalty for infeasible

def normalize_fitness(fitnessArr):
    # normalize fitness array
    maxFitness = max(fitnessArr)
    f = []
    for fitness in fitnessArr:
        f.append(1 - fitness/maxFitness)
        
    return f

def selection_pair(population, fitnessArr):
    pop = deepcopy(population)
    fit = deepcopy(fitnessArr)
    
    parent1 = choices(
                population =    pop, 
                weights =       fit,
                k = 1
            )[0]

    del fit[pop.index(parent1)]
    del pop[pop.index(parent1)]
    
    parent2 = choices(
                population =    pop, 
                weights =       fit,
                k = 1
            )[0]
    
    print("Parents: ", population.index(parent1), population.index(parent2))

    return [parent1, parent2]

def single_point_crossover(parent1, parent2):
    if len(parent1) != len(parent2):
        raise Exception("Genomes not equal length")    
    
    p = randint(1, len(parent1) - 1)
    return parent1[:p] + parent2[p:], parent2[:p] + parent1[p:]
    
def mutate(genome):
    for index, gene in enumerate(genome):
        if gene == None:
            continue
            
        if random() < mutProb:
            if random() < prob_pick:
                genome[index] = gen_Pick()
            else:
                genome[index] = gen_Wait()
        
    return genome

# =============================================================================
# execution of GA
# =============================================================================
s = Simulation(pictures = False)
population = gen_Population(1)

# keep good solution
recordScore = 1000
record = []
bestScores = []

for generation in range(generations):
    print("--- GENERATION {} ---".format(generation))
    
    # determine fitness
    fitnessArr = []
    for genome in tqdm(population, position=0, leave=True, desc="Calc population fitness gen{}: ".format(generation)):
        f = fitness(s, genome)    
        fitnessArr.append(f)
        
    # keep best fitness:
    bestScore = min(fitnessArr)
    bestGenome = population[fitnessArr.index(bestScore)]
    
    bestScores.append(bestScore)
    
    if bestScore < recordScore:
        record = deepcopy(bestGenome)
        recordScore = bestScore
        
    # generate children: crossover
    newPopulation = []
    for _ in range(round(popSize / 2)):
        parents = selection_pair(population, normalize_fitness(fitnessArr))
        child1, child2 = single_point_crossover(parents[0], parents[1])
        newPopulation.append(child1)
        newPopulation.append(child2)
        
    # mutation:
    for i, x in enumerate(newPopulation):
        mutate(newPopulation[i])
        
    # set new generation as population
    population = newPopulation
    
# execute the best one one last time, with pictures enabled:
print("Running record again ...")
fitness(s, record, save=True)  
