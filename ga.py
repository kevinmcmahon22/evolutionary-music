
from deap import base, creator, tools
from matplotlib import pyplot as plt
import random
import music

class GA:
    '''
    Define GA and helper functions for bassline evolution
    '''

    def __init__(self, num_gens, pop_size, tourn_size, hof_size, prob_cx, prob_mut, changes, testing=False):

        self.NGEN = num_gens
        self.POP_SIZE = pop_size
        self.TOURN_SIZE = tourn_size
        self.NUM_PARENTS = self.POP_SIZE // self.TOURN_SIZE # Must be even number, evenly divisible by tournament size
        self.HOF_SIZE = hof_size
        self.P_CX = prob_cx
        self.P_MUT = prob_mut
        self.CHANGES = changes
        self.TESTING = testing

        # Create toolbox
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()
        self.toolbox.register("attribute", music.random_note)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attribute, n=self.CHANGES.BASS_LEN)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual, n=self.POP_SIZE)
        # self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mate", tools.cxOnePoint)
        self.toolbox.register("selectParents", tools.selTournament, tournsize=self.TOURN_SIZE, k=self.NUM_PARENTS)
        # self.toolbox.register("selectParents", tools.selRoulette, k=self.NUM_PARENTS)
        # self.toolbox.register("selectParents", tools.selBest, k=self.NUM_PARENTS)
        self.toolbox.register("selectSurvivors", tools.selBest, k=self.POP_SIZE)

    # def print_plot(self, fit_by_gen):
    #     '''
    #     Print a plot showing fitness by generation
    #     '''
    #     generations = [i+1 for i in range(len(fit_by_gen))]
    #     plt.plot(generations, fit_by_gen)
    #     plt.title(f'Average Fitness by generation, population={self.POP_SIZE}')
    #     plt.xlabel('Generation')
    #     plt.ylabel('Fitness')

    def run_GA(self):
        '''
        Run the GA specified by parameters input in constructor
        '''

        # Initialize population
        pop = self.toolbox.population()
            
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
            print(best_bassline)
            print(best_bassline.fitness.values)
            
            c_score = music.generate_composition(best_bassline, self.CHANGES, transpose=24)
            music.generate_score(c_score, 'goat.png')
            c = music.generate_composition(best_bassline, self.CHANGES)
            music.play_composition(c)

        return avg_fit_of_gen
