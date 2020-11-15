from deap import gp
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

# Generate a tree


min_height = 3
max_height = 5

expr = gp.genFull(musicgp, min_height, max_height)
# expr = gp.genGrow(musicgp, min_height, max_height)
# expr = gp.genHalfAndHalf(musicgp, min_height, max_height)
tree = gp.PrimitiveTree(expr)
str(tree)
function = gp.compile(tree, musicgp)
print(function)
