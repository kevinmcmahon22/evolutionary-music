
from deap import base, creator, tools
from matplotlib import pyplot as plt
import random
import music
import time

class GA:
    '''
    Define GA and helper functions for bassline evolution
    '''

    def __init__(self, num_gens, pop_size, tourn_size, hof_size, prob_cx, prob_mut, changes, songtitle='', testing=False):

        self.NGEN = num_gens
        self.POP_SIZE = pop_size
        self.TOURN_SIZE = tourn_size
        self.NUM_PARENTS = self.POP_SIZE // self.TOURN_SIZE
        # Number of parents must be even
        if self.NUM_PARENTS % 2 == 1:
            self.NUM_PARENTS += 1
        self.HOF_SIZE = hof_size
        self.P_CX = prob_cx
        self.P_MUT = prob_mut
        self.CHANGES = changes
        self.TESTING = testing
        self.SONG_TITLE = songtitle

        # Create toolbox
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("attribute", music.random_note)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attribute, n=self.CHANGES.BASS_LEN)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual, n=self.POP_SIZE)
        # self.toolbox.register("mate", tools.cxOnePoint)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("selectParents", tools.selTournament, tournsize=self.TOURN_SIZE, k=self.NUM_PARENTS)
        # self.toolbox.register("selectParents", tools.selRoulette, k=self.NUM_PARENTS)
        # self.toolbox.register("selectParents", tools.selRandom, k=self.NUM_PARENTS)
        # self.toolbox.register("selectParents", tools.selBest, k=self.NUM_PARENTS)
        self.toolbox.register("selectSurvivors", tools.selBest, k=self.POP_SIZE)

    def print_plot(self, best_inds):
        '''
        Print a plot of the list best_inds
        '''
        generations = [i+1 for i in range(len(best_inds))]
        plt.plot(generations, best_inds)
        plt.title(f'Average Fitness for {self.SONG_TITLE} by Generation')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.grid(True)
        plt.savefig(f'{self.SONG_TITLE}_plot.png')
        plt.close()

    def run_GA(self):
        '''
        Run the GA specified by parameters input in constructor
        '''

        start_ga_time = time.time()

        # Initialize population
        pop = self.toolbox.population()

        # Evaluate initial population, here so Roulette selection will work
        fitnesses = [music.evaluate_bassline(ind, self.CHANGES) for ind in pop]
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

            # Crossover
            for child1, child2 in zip(parents[::2], parents[1::2]):
                if random.random() < self.P_CX:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Mutation
            for mutant in pop:
                if random.random() < self.P_MUT:
                    # mutant = self.toolbox.mutate(mutant)
                    mutant = music.mutate_bassline(mutant, self.CHANGES)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            # fitnesses = map(music.evaluate_bassline, invalid_ind)
            fitnesses = [music.evaluate_bassline(ind, self.CHANGES) for ind in invalid_ind]
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
            avg_fit /= self.POP_SIZE
            avg_fit_of_gen.append(avg_fit)
        
        # 
        # Output results of GA
        # 
        
        if not self.TESTING:
            
            best_bassline = hof[0]
            # print(best_bassline)
            print(best_bassline.fitness.values)

            self.print_plot(avg_fit_of_gen)
            
            c_score = music.generate_composition(best_bassline, self.CHANGES, transpose=24)
            music.generate_score(c_score, f'{self.SONG_TITLE}.png')
            c_wav = music.generate_composition(best_bassline, self.CHANGES, transpose=-12)
            music.create_wav_file(self.SONG_TITLE, c_wav)

            print('GA execution time:', time.time() - start_ga_time)
            
            # music.play_composition(c)

        return avg_fit_of_gen
