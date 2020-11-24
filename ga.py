# 
# Evolutionary Music in Python
# 
# CSE 848 semester project
# 
# Kevin McMahon
# 
# Define GA and helper functions for bassline evolution
# 

from deap import base, creator, tools
from matplotlib import pyplot as plt
import random
import music


class GA:

    def __init__(self):

        # Koza Tableau
        self.P_CX = 0.1
        self.P_MUT = 0.05
        self.NGEN = 500
        self.POP_SIZE = 100
        self.TOURN_SIZE = 3
        self.NUM_PARENTS = self.POP_SIZE // self.TOURN_SIZE # Must be even number, evenly divisible by tournament size
        self.HOF_SIZE = 1

        # Create toolbox
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("attribute", music.random_note)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attribute, n=music.get_bassline_len)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual, n=self.POP_SIZE)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("selectParents", tools.selTournament, tournsize=self.TOURN_SIZE, k=self.NUM_PARENTS)
        self.toolbox.register("selectSurvivors", tools.selBest, k=self.POP_SIZE)
        self.toolbox.register("mutate", self.mutation)
        self.toolbox.register("evaluate", self.evaluation)

    def mutation(bassline):
        return music.mutate_bassline(bassline)

    def evaluation(self):
        return music.evaluate_bassline(self),

    def print_plot(best_inds):
        '''
        Print a plot of the list best_inds
        '''
        generations = [i+1 for i in range(len(best_inds))]
        plt.plot(generations, best_inds)
        plt.title(f'Average Fitness by generation, population={POP_SIZE}')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')


    def run_GA(self):
        '''
        Run the GA specified by parameters input in constructor
        '''

        # Initialize and evaluate population
        pop = self.toolbox.population(n=self.POP_SIZE)
        fitnesses = map(self.toolbox.evaluate, pop)
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
            
        # Initialize HOF and average fitness list
        hof = tools.HallOfFame(self.HOF_SIZE)
        avg_fit_of_gen = []

        # Execute generations
        for gen in range(self.NGEN):
            # Select the next generation individuals
            parents = self.toolbox.selectParents(pop)

            # make copy of parents and add back to population to preserve elites
            parents_clone = map(self.toolbox.clone, parents)
            
            # add to population since crossover/mutation of original 
            pop.extend(parents_clone)

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(parents[::2], parents[1::2]):
                if random.random() < P_CX:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in pop:
                if random.random() < P_MUT:
                    mutant = self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            # Survivor selection, Elitism is used
            pop[:] = self.toolbox.selectSurvivors(pop)
            
            # Update hall of fame
            hof.update(pop)
            
            # Track average fitness of each generation
            avg_fit = 0
            for individual in pop:
                avg_fit += individual.fitness.values[0]
            avg_fit /= POP_SIZE
            avg_fit_of_gen.append(avg_fit)
            
        # Output results of ga run
        print(hof[0])
        print_plot(avg_fit_of_gen)
        music.play_bassline(hof[0])
        music.generate_score(hof[0], 'goat.png')



# 
# Koza Tableau
# 

# P_CX = 0.1
# P_MUT = 0.05

# NGEN = 500
# POP_SIZE = 100
# TOURN_SIZE = 3
# NUM_PARENTS = POP_SIZE // TOURN_SIZE # Must be even number, evenly divisible by tournament size

# HOF_SIZE = 1


# def random_note():
#     '''
#     Use the toolbox for init because list object doesn't have fitness atomatically included
#     '''
#     return music.random_note()

# def mutation(bassline):
#     return music.mutate_bassline(bassline)

# def evaluation(self):
#     return music.evaluate_bassline(self),

# def print_plot(best_inds):
#     generations = [i+1 for i in range(len(best_inds))]
#     plt.plot(generations, best_inds)
#     plt.title(f'Average Fitness by generation, population={POP_SIZE}')
#     plt.xlabel('Generation')
#     plt.ylabel('Fitness')


# creator.create("FitnessMax", base.Fitness, weights=(1.0,))
# creator.create("Individual", list, fitness=creator.FitnessMax)

# toolbox = base.Toolbox()
# toolbox.register("attribute", random_note)
# toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=music.get_bassline_len())
# toolbox.register("population", tools.initRepeat, list, toolbox.individual)
# toolbox.register("mate", tools.cxTwoPoint)
# toolbox.register("selectParents", tools.selTournament, tournsize=TOURN_SIZE, k=NUM_PARENTS)
# toolbox.register("selectSurvivors", tools.selBest, k=POP_SIZE)
# toolbox.register("mutate", mutation)
# toolbox.register("evaluate", evaluation)


# # Initialize and evaluate population
# pop = toolbox.population(n=POP_SIZE)
# fitnesses = map(toolbox.evaluate, pop)
# for ind, fit in zip(pop, fitnesses):
#     ind.fitness.values = fit
    
# # Initialize HOF
# hof = tools.HallOfFame(HOF_SIZE)

# best_of_gen = []
# avg_fit_of_gen = []

# for gen in range(NGEN):
#     # Select the next generation individuals
#     parents = toolbox.selectParents(pop)

#     # make copy of parents and add back to population to preserve elites
#     parents_clone = map(toolbox.clone, parents)
    
#     # add to population since crossover/mutation of original 
#     pop.extend(parents_clone)

#     # Apply crossover and mutation on the offspring
#     for child1, child2 in zip(parents[::2], parents[1::2]):
#         if random.random() < P_CX:
#             toolbox.mate(child1, child2)
#             del child1.fitness.values
#             del child2.fitness.values

#     for mutant in pop:
#         if random.random() < P_MUT:
#             mutant = toolbox.mutate(mutant)
#             del mutant.fitness.values

#     # Evaluate the individuals with an invalid fitness
#     invalid_ind = [ind for ind in pop if not ind.fitness.valid]
#     fitnesses = map(toolbox.evaluate, invalid_ind)
#     for ind, fit in zip(invalid_ind, fitnesses):
#         ind.fitness.values = fit
    
#     # Survivor selection, Elitism is used
#     pop[:] = toolbox.selectSurvivors(pop)
    
#     # Update hall of fame
#     hof.update(pop)
#     best_of_gen.append(hof[0].fitness.values)
    
#     # Track average fitness of each generation
#     avg_fit = 0
#     for individual in pop:
#         avg_fit += individual.fitness.values[0]
#     avg_fit /= POP_SIZE
#     avg_fit_of_gen.append(avg_fit)
    
# # Output results of ga run
# print_plot(avg_fit_of_gen)
# print(hof[0])
# music.play_bassline(hof[0])
# music.generate_score(hof[0], 'goat.png')
