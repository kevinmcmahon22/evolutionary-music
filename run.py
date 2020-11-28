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
import numpy as np
from matplotlib import pyplot as plt
import time


class Run:
    
    def __init__(self, num_runs=1):
        
        # 
        # Koza Tableau
        # 
        
        self.KOZA = {
            'num_gens'   : 500,
            'pop_size'   : 100,
            'tourn_size' : 3,
            'hof_size'   : 1,
            'prob_cx'    : 0.1,
            'prob_mut'   : 0.05,   
        }
        
        self.INIT_KOZA = self.KOZA
        
        # Create Progression object
        if len(sys.argv) != 2:
            sys.exit('FileNotSuppliedError: Must supply name of text file contatining a chord progression')
        self.CHANGES = Progression(sys.argv[1])
        # self.CHANGES = Progression('blues.txt')
        
        self.NUM_RUNS = num_runs
        
    def display_plot(self, fitness_by_gen, variable_name, values):
        '''
        Print a plot the average fitness by generation for NUM_RUNS iterations
        '''
        generations = [i for i in range(self.KOZA["num_gens"])]
        plt.figure(figsize=(16,8))
        plt.rcParams.update({'font.size': 12})
        for tup in fitness_by_gen:
            plt_label = tup[0]
            if type(tup[0]) == float:
                plt_label = round(tup[0], 2)
            plt.plot(generations, tup[1], label=plt_label)
        plt.title(f'Average Fitness by Generation, Varying {variable_name}\ngens={self.KOZA["num_gens"]}, runs={self.NUM_RUNS}')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend(loc='lower right')
        plt.savefig(f'./plots/{variable_name}{values[0]}_{self.KOZA[variable_name]}__{self.KOZA["num_gens"]}gens_{self.NUM_RUNS}runs.png')
        plt.close()
    
    def one_run(self):
        ga = GA(*self.KOZA.values(), self.CHANGES)
        ga.run_GA()

    def test(self, testing_list):
        
        for variable_name, values in testing_list:
            
            # Restore variables to their initial values
            self.KOZA = self.INIT_KOZA
            
            fitness_by_gen = []
            
            start = values[0]
            stop  = values[1]
            step  = values[2]
            current_val  = start
            
            while current_val <= stop:
                
                self.KOZA[variable_name] = current_val
                
                # Added flag to suppress MIDI output when testing
                ga = GA(*self.KOZA.values(), self.CHANGES, True)
                
                # run GA for specified number of runs with this set of variable values
                fit_by_run = [0] * self.KOZA["num_gens"]
                for i in range(self.NUM_RUNS):
                    avg_fit = ga.run_GA()
                    fit_by_run = np.add(fit_by_run, avg_fit)

                fit_by_run = np.divide(fit_by_run, self.NUM_RUNS)
                
                fitness_by_gen.append( (f'{self.KOZA[variable_name]}', fit_by_run) )
                
                current_val += step
            
            # Output results for each list index to it's own plot
            self.display_plot(fitness_by_gen, variable_name, values)
            

# 
# Generate a single bassline
# 

# start = time.time()
# runner = Run()
# runner.one_run()
# print("Execution time: ", time.time() - start)

# 
# Run testing suite, output results on one plot for each variable tested
# 

# Keep size of legend in mind when choosing range for variables

testing_list = [(
    'pop_size' , [10, 150, 10]        ),(
    'pop_size' , [50, 1000, 50]       ),(
    'prob_cx'  , [0.05, 0.8, 0.05]    ),(
    'prob_mut' , [0.05, 0.8, 0.05]    ),(
    'num_gens' , [100, 2000, 100]     )
]

start = time.time()
runner = Run(50)
runner.test(testing_list)
print("Testing time: ", time.time() - start)
