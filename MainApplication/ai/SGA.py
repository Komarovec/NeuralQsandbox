from objs.CarAI import CarAI
from ai.models import SequentialModel

class SGA():
    def __init__(self, input_space, output_space, pop_size=100, mutation_rate=0.01, population=None):
        #Basic variables
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate

        self.population = population

        #AI
        self.input_space = input_space
        self.output_space = output_space

    #Generates random population
    def randomPopulation(self):
        self.population = []
        for _ in range(self.pop_size):
            self.population.append()

    