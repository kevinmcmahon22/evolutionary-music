import random
from deap import base, creator, tools

import music

import mingus.core.progressions as progressions




# Individuals start as sequence of quarter notes
# Define function to randomly change a quarter note to eighth notes or triplet

# Population is list of tuples, each tuple is note followed by duration (default to 1)

# Perform operations on a single key, then transpose to a new key when
# evolution terminates


# Why GA? When learning music a player will start off playing random notes
# Then an instructor or other player guides them toward a better musical line
# I wanted to define simple operators to build from random solution to a random but pleasant baseline

# GP kept giving me too many errors and very limited documentation




# Koza Tableau

# 4 quarter notes * 12 measures to start
BASE_LEN = 8

P_CX = 0.5

# Probability of mutating a melody, then prob mutating each individual note
P_MUT = 0.4
P_MUT_NOTE = 0.1

# half, whole, m3, M3, 4th, 5th
MUT_STEPS = [-1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -7, 7]

# C0 to B1, C2 is 48
MIN_NOTE = 24
MAX_NOTE = 47

NGEN = 5

POP_SIZE = 50



# Mutation operators

# No tritone or larger than fifth becuase those don't make sense musically
# Inspired by possible baseline intervals on a fretboard



def stepwise(baseline, note_index, interval):
    
    previous_note = baseline[note_index]

    baseline[note_index] += interval  
    
    # if note is out of playable range, then keep original note
    if baseline[note_index] < MIN_NOTE or baseline[note_index] > MAX_NOTE:
        baseline[note_index] = previous_note
    
    return baseline

def quarter_to_triplets(baseline, note_index):
    pass

def quarter_to_eighths(baseline, note_index):
    pass

MUT_FUNC_NAME = [stepwise, quarter_to_triplets, quarter_to_eighths]


def mutation(baseline):
    
    # Mutate about 10% of notes using a random mutation function
    for note_index in range(len(baseline)):
        if random.random() < P_MUT_NOTE:
            
            interval = random.choice(MUT_STEPS)
    
            baseline = stepwise(baseline, note_index, interval)
    
    return baseline


# Single and double crossover should work fine


# I want to make evaluation simple but robust, this will be hardest part

# 1. play root
# 2. play any note of chord/scale
# 3. play any note, new note
# 4. leading tone: half, whole, fifth

# each note should be within a fourth of the previous note, otherwise penalty

# 

# 1 2 3 5
# 4 3 2 1

# move up/down arpegio

def evaluate(individual):
    return music.evaluate_baseline(individual),


def random_note():
    return random.randint(MIN_NOTE, MAX_NOTE)


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attribute", random_note)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=BASE_LEN)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

toolbox.register("bestInd", tools.selBest)


# Get input file as command arg, read in text file of multiple lines
# progression = 

# Initialize population
pop = toolbox.population(n=POP_SIZE)

# Evaluate the entire population
fitnesses = map(toolbox.evaluate, pop)
for ind, fit in zip(pop, fitnesses):
    ind.fitness.values = fit
    

for g in range(NGEN):
    # Select the next generation individuals
    offspring = toolbox.select(pop, len(pop))

    # Clone the selected individuals
    # error, map object is not subscriptable
    # offspring = map(toolbox.clone, offspring)

    # Apply crossover and mutation on the offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < P_CX:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    for mutant in offspring:
        if random.random() < P_MUT:
            # toolbox.mutate(mutant)
            mutant = mutation(mutant)
            del mutant.fitness.values

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # The population is entirely replaced by the offspring
    pop[:] = offspring
    
    best_ind = toolbox.bestInd(pop, 1)[0]
    print(best_ind)
    
    # music.play_baseline(best_ind)
