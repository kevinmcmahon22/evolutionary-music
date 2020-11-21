from deap import gp, base, creator, tools
from matplotlib import pyplot as plt
import pygraphviz as pgv
import operator
import random

import functionset as func



def evaluate(individual, pset):
    # Return int/tuple of int with fitness values
    num = gp.compile(individual, pset)
    return num,

def function_set():
    return func.getFunctionSet()

def terminal_set():
    return func.getTerminalSet()

def print_tree(expr, filename):
    nodes, edges, labels = gp.graph(expr)

    g = pgv.AGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    g.layout(prog="dot")
    
    for i in nodes:
        n = g.get_node(i)
        n.attr["label"] = labels[i]
    
    g.draw(f'{filename}.png')
    
def print_plot(best_inds):
    generations = [i+1 for i in range(len(best_inds))]
    plt.plot(generations, best_inds)
    for b in best_inds:
        print(b)

    

# Loosely typed GP
pset = gp.PrimitiveSet("main", 0)

# Add function and terminal sets
for function in function_set():
    pset.addPrimitive(function[0], function[1])
for terminal in terminal_set():
    pset.addTerminal(terminal)


# Declare fitness and individuals
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax, pset=pset)


# Koza tableau variables for GP run
pop_size = 20
num_parents = 4
tourn_select_size = 3
p_mut = 0.01
p_xover = 1
num_gens = 40
tourn_size = 3
min_height = 3
max_height = 5
max_tree_height = 7
max_num_nodes = 50

best_sols = []

# Register operators
toolbox = base.Toolbox()
toolbox.register("generateGp", gp.genFull, pset=pset, min_=min_height, max_=max_height)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.generateGp)

# Use bag population, no inherent ordering
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Create Hall of Fame
toolbox.register("goat", tools.HallOfFame)

# Methods
toolbox.register("mate", gp.cxOnePoint) # 0.1 prob mutate leaf node
toolbox.register("mutate", gp.mutNodeReplacement, pset=pset)
toolbox.register("parentSelect", tools.selTournament, tournsize=tourn_select_size)
# toolbox.register("parentSelect", tools.selRoulette)
toolbox.register("childSelect", tools.selBest, k=pop_size)
toolbox.register("evaluate", evaluate)

# Bloat control
toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter('height'), max_value=max_tree_height))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter('height'), max_value=max_tree_height))
# toolbox.decorate("mate", gp.staticLimit(len, max_value=max_num_nodes))
# toolbox.decorate("mutate", gp.staticLimit(len, max_value=max_num_nodes))



# Initialize population
population = toolbox.population(n=pop_size)


for cur_gen in range(num_gens):
     
    # Parent selection
    parents = toolbox.parentSelect(population, num_parents)
    
    # Crossover
    for i in range(1, len(parents), 2):
        if random.random() < p_xover:
            # print(parents[i-1])
            # print(parents[i])
            # print_tree(parents[i-1], 'p1')
            # print_tree(parents[i], 'p2')
            tup = toolbox.mate(parents[i-1], parents[i])
            population.extend([tup[0], tup[1]])
            # del parents[i-1].fitness.values
            # del parents[i].fitness.values
    
    # for child1, child2 in zip(population[::2], population[1::2]):
    #     if random.random() < p_xover:
    #         copy1 = toolbox.clone(child1)
    #         copy2 = toolbox.clone(child2)
    #         population.extend([copy1, copy2])
    #         toolbox.mate(child1, child2)
    #         del child1.fitness.values
    #         del child2.fitness.values
        
    # Mutation
    for mutant in population:
        if random.random() < p_mut:
            toolbox.mutate(mutant)
            del mutant.fitness.values
    
    # Evaluate fitness
    for ind in population:
        # only evaluate fitness if it has been changed
        if ind.fitness.values == ():
            ind.fitness.values = evaluate(ind, pset)
        
    # Survivor selection
    population = toolbox.childSelect(population)
    
    # Hall of fame
    toolbox.goat(population)
    
    

    # Add best solution to list to print
    best_ind = tools.selBest(population, 1)[0]
    best_ind_fit = gp.compile(best_ind, pset)
    best_sols.append(best_ind_fit)
    # print_tree(best_ind)

print_plot(best_sols)

print(toolbox.goat)

# goat = tools.selBest(population, 1)[0]
# print_tree(goat, 'goat')