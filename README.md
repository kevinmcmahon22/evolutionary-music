# Generating Basslines for a 12-bar Blues using Evolutionary Methods
Course project for CSE 848: Evolutionary Computation

### Software
* FluidSynth - https://github.com/FluidSynth/fluidsynth/releases
* MIDI soundfont *FluidR3_GM.sf* - https://github.com/urish/cinto/tree/master/media
* DEAP - https://deap.readthedocs.io/en/master/
* mingus - https://bspaans.github.io/python-mingus/

### Python files
* ga - contains a class that creates and runs an instance of a Genetic Algorithm
* gp - use Genetic Programming rather than GA, incomplete
* music - functions handling all music related tasks
* progression - creates a class that represents a progression (from dir progressions)
* run - starting point of system, can run tests on operators or generate sample basslines

### Subdirectories
* figures - images and screenshots used in the formal report for this project
* plots - tests comparing parent selection operators, mutation/crossover probabilities, and population size
* progressions - input files with progressions to evolve basslines over
