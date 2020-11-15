from deap import gp, base, creator, tools
import pygraphviz as pgv
import operator

# Loosly typed typed GP
# Functions can return a int/string or list of int/string

# No args to set, want to generate unique individuals with no args
musicgp = gp.PrimitiveSet("main", 0)
# musicgp.renameArguments(ARG0="x")
# musicgp.renameArguments(ARG1="y")

# Add functions, reference Alpern 1994
function_set = [(max, 2), (operator.add, 2), (operator.mul, 2)]
for f in function_set:
    musicgp.addPrimitive(f[0], f[1])


# Add valid notes as possible terminals
terminal_set = [1, 2]
for t in terminal_set:
    musicgp.addTerminal(t)


# Create fitness and individual functions
creator.create("FitnessMax", base.Fitness, weights=(1.0, 1.0))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax, pset=musicgp)


# Create toolbox for one line individual creation
toolbox = base.Toolbox() 
# Full, Grow, HalfAndHalf
min_height = 3
max_height = 5
toolbox.register("generateGpFull", gp.genHalfAndHalf, pset=musicgp, min_=min_height, max_=max_height)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.generateGpFull)


# Evaluation
# compile each individual and get list representation
expr = toolbox.individual()
num = gp.compile(expr, musicgp)

# Call evaluate function, returns a tuple of fitness of various parameters


# def evaluate(individual):
#     # Do some hard computing on the individual
#     a = sum(individual)
#     b = len(individual)
#     return a, 1. / b

# ind1.fitness.values = evaluate(ind1)
# print ind1.fitness.valid    # True
# print ind1.fitness          # (2.73, 0.2)
# print(num)



# Print tree to png
nodes, edges, labels = gp.graph(expr)

g = pgv.AGraph()
g.add_nodes_from(nodes)
g.add_edges_from(edges)
g.layout(prog="dot")

for i in nodes:
    n = g.get_node(i)
    n.attr["label"] = labels[i]

g.draw("tree.png")
