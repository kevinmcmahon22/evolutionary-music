from deap import gp, base, creator, tools
from matplotlib import pyplot as plt
import pygraphviz as pgv
import operator
import random



def evaluate(individual, pset):
    # Return int/tuple of int with fitness values
    num = gp.compile(individual, pset)
    return num,

def get_function_set():
    return [(max, 2), (operator.add, 2), (operator.mul, 2)]

def get_terminal_set():
    return [3, 2]

def init_population(toolbox, pop_size):
    population = []
    for n in range(pop_size):
        population.append(toolbox.individual())
    return population

def print_tree(expr):
    nodes, edges, labels = gp.graph(expr)

    g = pgv.AGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    g.layout(prog="dot")
    
    for i in nodes:
        n = g.get_node(i)
        n.attr["label"] = labels[i]
    
    g.draw("tree.png")
    
def print_plot(best_inds):
    generations = [i+1 for i in range(len(best_inds))]
    plt.plot(generations, best_inds)
    for b in best_inds:
        print(b)

    

# Loosely typed GP
pset = gp.PrimitiveSet("main", 0)

# Add function and terminal sets
for func in get_function_set():
    pset.addPrimitive(func[0], func[1])
for term in get_terminal_set():
    pset.addTerminal(term)


# Declare fitness and individuals
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax, pset=pset)


# Koza tableau variables for GP run
pop_size = 10
num_parents = 4
tourn_select_size = 3
p_mut = 0.01
p_xover = 0.5
num_gens = 100
tourn_size = 3
min_height = 3
max_height = 5
max_tree_height = 17

best_sols = []

# Register operators
toolbox = base.Toolbox()
toolbox.register("generateGp", gp.genHalfAndHalf, pset=pset, min_=min_height, max_=max_height)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.generateGp)
toolbox.register("mate", gp.cxOnePointLeafBiased, termpb=0.1) # 0.1 prob mutate leaf node
toolbox.register("mutate", gp.mutNodeReplacement, pset=pset)
toolbox.register("parentSelect", tools.selTournament, tournsize=tourn_select_size)
toolbox.register("childSelect", tools.selBest, k=pop_size)
toolbox.register("evaluate", evaluate)

# toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=max_tree_height))
# toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=max_tree_height))
# toolbox.decorate("mate", gp.staticLimit(len, max_value=max_tree_height))
# toolbox.decorate("mutate", gp.staticLimit(len, max_value=max_tree_height))

# Initialize population
population = init_population(toolbox, pop_size)

for cur_gen in range(num_gens):
     
    
    offspring = [toolbox.clone(ind) for ind in population]
    
    # Parent selection
    parents = toolbox.parentSelect(offspring, num_parents)     
    
    # Crossover
    for i in range(1, len(parents), 2):
        if random.random() < p_xover:
            offspring[i-1], offspring[i] = toolbox.mate(offspring[i-1], parents[i])
            del offspring[i-1].fitness.values
            del offspring[i].fitness.values
    
    # for child1, child2 in zip(population[::2], population[1::2]):
    #     if random.random() < p_xover:
    #         copy1 = toolbox.clone(child1)
    #         copy2 = toolbox.clone(child2)
    #         population.extend([copy1, copy2])
    #         toolbox.mate(child1, child2)
    #         del child1.fitness.values
    #         del child2.fitness.values
        
    # Mutation
    for mutant in offspring:
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

    # Add best solution to list to print
    best_ind = tools.selBest(population, 1)[0]
    best_ind_fit = gp.compile(best_ind, pset)
    best_sols.append(best_ind_fit)
    # print_tree(best_ind)

print_plot(best_sols)

goat = tools.selBest(population, 1)[0]
print_tree(goat)