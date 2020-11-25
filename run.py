# 
# Evolutionary Music in Python
# 
# CSE 848 semester project
# 
# Kevin McMahon
# 

from ga import GA
from progression import Progression
import sys


# Koza Tableau
num_gens = 500
pop_size = 100
tourn_size = 3
hof_size = 1
prob_cx = 0.1
prob_mut = 0.05


# Create Progression object
if len(sys.argv) != 2:
    sys.exit('FileNotSuppliedError: Must supply name of text file contatining a chord progression')
changes = Progression(sys.argv[1])

# Create GA object
ga = GA(num_gens, pop_size, tourn_size, hof_size, prob_cx, prob_mut, changes)

# Run GA and output results
ga.run_GA()