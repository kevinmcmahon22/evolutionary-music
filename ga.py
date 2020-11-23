import random
from deap import base, creator, tools

import music

from matplotlib import pyplot as plt



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

P_CX = 0.1

# Probability of mutating a melody, then prob mutating each individual note
P_MUT = 0.05
P_MUT_NOTE = 0.05

# half, whole, m3, M3, 4th, 5th
MUT_STEPS = [-1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -7, 7]

# C0 to B1, C2 is 48
MIN_NOTE = 24
MAX_NOTE = 47

NGEN = 500

POP_SIZE = 100

TOURN_SIZE = 3

# Must be even number, evenly divisible by tournament size
NUM_PARENTS = POP_SIZE // TOURN_SIZE

HOF_SIZE = 1


# 4 quarter notes * 12 measures to start
# BASE_LEN = len(BLUES_12 * 4)
BASE_LEN = 48


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


def mutation(bassline):
    
    for note_index in range(len(bassline)):
        if random.random() < P_MUT_NOTE:
            
            interval = random.choice(MUT_STEPS)
    
            # baseline = stepwise(baseline, note_index, interval)
            
            previous_note = bassline[note_index]

            bassline[note_index] += interval  
            
    
            # if note is out of playable range, then keep original note
            if bassline[note_index] < MIN_NOTE or bassline[note_index] > MAX_NOTE:
                bassline[note_index] = previous_note
                
            
            # also keep original if new note creates bad interval
            if note_index > 0:
                new_jump = abs(bassline[note_index] - bassline[note_index - 1])
                if new_jump > 5 or new_jump == 6:
                    bassline[note_index] = previous_note
            if note_index < len(bassline) - 1:
                new_jump = abs(bassline[note_index] - bassline[note_index + 1])
                if new_jump > 5 or new_jump == 6:
                    bassline[note_index] = previous_note
                    
                    
            if note_index > 0 and note_index < len(bassline) - 1:            
                next_note = bassline[note_index + 1]
                prev_note = bassline[note_index - 1]
                curr_note = bassline[note_index]
                
                # new note should be between prev and next, rising or falling             
                if curr_note < next_note and curr_note > prev_note:
                    pass
                elif curr_note < prev_note and curr_note > next_note:
                    pass
                else:
                    # forgive with 20% prob, otherwise replace
                    if random.random() < 0.01:
                        bassline[note_index] = previous_note
                    
                # keep if note is now identical to next or previous
                if next_note == prev_note or next_note == curr_note:
                    bassline[note_index] = previous_note
                            
            
            # Add in eighths and triplets when quarters down solid
    
    return bassline


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

# Evolve in key of C, transpose to different key for playback

def evaluate(individual):
    return music.evaluate_baseline(individual),



def random_note():
    return random.randint(MIN_NOTE+5, MAX_NOTE-5)
    # return MIN_NOTE + 12


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attribute", random_note)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=BASE_LEN)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("mate", tools.cxTwoPoint)
# toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("selectParents", tools.selTournament, tournsize=TOURN_SIZE, k=NUM_PARENTS)
toolbox.register("selectSurvivors", tools.selBest, k=POP_SIZE)
toolbox.register("evaluate", evaluate)

toolbox.register("bestInd", tools.selBest)

# toolbox.register("hof", tools.HallOfFame, maxsize=HOF_SIZE)


# Get input file as command arg, read in text file of multiple lines
# progression = 

# Initialize population
pop = toolbox.population(n=POP_SIZE)

# Evaluate the entire population
fitnesses = map(toolbox.evaluate, pop)
for ind, fit in zip(pop, fitnesses):
    ind.fitness.values = fit
    
# Initialize HOF
hof = tools.HallOfFame(HOF_SIZE)

best_of_gen = []
avg_fit_of_gen = []


# 
# NO ELITISM
# ELITISM MAY BE A GOOD IDEA AFTER ALL
# 

def print_plot(best_inds):
    generations = [i+1 for i in range(len(best_inds))]
    plt.plot(generations, best_inds)
    plt.title(f'Average Fitness by generation, population={POP_SIZE}')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    # for b in best_inds:
    #     print(b)

for gen in range(NGEN):
    # Select the next generation individuals
    parents = toolbox.selectParents(pop)

    # make copy of parents
    parents_clone = map(toolbox.clone, parents)
    
    # add to population since crossover/mutation of original 
    pop.extend(parents_clone)

    # Apply crossover and mutation on the offspring
    for child1, child2 in zip(parents[::2], parents[1::2]):
        if random.random() < P_CX:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values
            
    # print(x == parents)
    # offspring = parents
    
    # # Add offspring to population
    # pop.extend(parents)

    for mutant in pop:
        if random.random() < P_MUT:
            # toolbox.mutate(mutant)
            mutant = mutation(mutant)
            del mutant.fitness.values

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # The population is entirely replaced by the offspring
    # pop[:] = offspring
    
    # Survivor selection
    pop[:] = toolbox.selectSurvivors(pop)
    
    # Update hall of fame
    hof.update(pop)
    # print(hof[0], hof[0].fitness.values)
    
    best_of_gen.append(hof[0].fitness.values)
    
    # add to list of average population
    avg_fit = 0
    for individual in pop:
        avg_fit += individual.fitness.values[0]
    avg_fit /= POP_SIZE
    avg_fit_of_gen.append(avg_fit)
    

print_plot(avg_fit_of_gen)
print(hof[0])
music.play_baseline(hof[0])
music.generate_score(hof[0], 'goat.png')
    
# print(best_ind, '\n', best_ind.fitness.values)
