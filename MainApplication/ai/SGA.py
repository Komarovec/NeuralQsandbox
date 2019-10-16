from objs.CarAI import CarAI
from ai.models import SequentialModel

import numpy as np

class SGA():
    def __init__(self, pop_size=10, mutation_rate=0.1, population=[]):
        #Max reward
        self.highestReward = 0
        self.highestRewardedModel = None

        #Avarage reward
        self.averageReward = 0

        #Basic variables
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.generation = 0

        self.population = population

    #Generates random population
    def randomPopulation(self, simulation):
        self.generation = 0

        self.population = []
        for _ in range(self.pop_size):
            self.population.append(simulation.addCarAI())

    #sort population by fitness
    def sortPopulation(self):
        self.population.sort(key=lambda x: x.reward, reverse=True)

    #Select best individuals from population
    def selectParents(self, hm_parents=2):
        parents = []

        #Sort population by fitness
        self.sortPopulation()

        #Pick n parents by best fitness
        for i in range(hm_parents):
            parents.append(self.population[i])

        return parents

    #Calculate average fitness
    def averageFitness(self):
        fitness_sum = 0
        for individual in self.population:
            fitness_sum += individual.reward

        fitness_average = fitness_sum / self.pop_size
        self.averageReward = fitness_average

        return fitness_average

    #Crossover
    def crossover(self, parents):
        for car in self.population:
            model = car.model

            #Iterate through layers
            for k, layer in enumerate(model.layers):
                new_weights_for_layer = []
                #Each layer has 2 matrizes, one for connection weights and one for biases
                #Then itterate through each matrix

                for j, weight_array in enumerate(layer.get_weights()):
                    #Save their shape
                    save_shape = weight_array.shape
                    #Reshape them to one dimension
                    one_dim_weight = weight_array.reshape(-1)

                    #Get weights from all parents
                    parentsWeights = []
                    for parent in parents:
                        pWeights = parent.model.layers[k].get_weights()[j]
                        pWeights = pWeights.reshape(-1)
                        parentsWeights.append(pWeights)

                    for i, _ in enumerate(one_dim_weight):
                        #Go through individual weights
                        #Pick random parent and set weight
                        parentIndex = np.random.randint(len(parents))
                        one_dim_weight[i] = parentsWeights[parentIndex][i]

                        #Random mutation
                        one_dim_weight[i] = self.mutateWeight(one_dim_weight[i], self.mutation_rate)

                    #Reshape them back to the original form
                    new_weight_array = one_dim_weight.reshape(save_shape)
                    
                    #Save them to the weight list for the layer
                    new_weights_for_layer.append(new_weight_array)

                #Set the new weight list for each layer
                model.layers[k].set_weights(new_weights_for_layer)

    #Mutation
    def mutateWeight(self, weight, mutation_rate):
        if(mutation_rate <= np.random.random()):
            return np.random.normal(loc=0,scale=1)
        else:
            return weight

    #Calculate fitness of a model
    def calculateFitness(self, car, simulation):
        dist = car.distToFinish(simulation)

        #When no finish found
        if(dist == None):
            fitness = 0

        #Calculate fitness based on distance to finish
        elif(dist != 0):
            fitness = fitness = 1/dist
            
        #If distance is 0 --> finish found
        else:
            fitness = fitness = 100000
            print("Solution found!")

        return fitness*10000

    #Create new population
    def newPopulation(self, simulation):
        #Calculate average reward
        self.averageFitness()

        #Selection --> select the best
        parents = self.selectParents()

        #Save the best model and his reward
        highestReward = parents[0].reward
        highestRewardedModel = parents[0]

        #Count only the best of the best
        if(self.highestReward < highestReward):
            self.highestReward = highestReward
            self.highestRewardedModel = highestRewardedModel

        #Make new population
        self.crossover(parents)

        #Respawn population
        for car in self.population:
            car.respawn(simulation)

        #Increment generation number
        self.generation += 1

    #Car died --> calculate fitness
    def carDied(self, car, simulation):
        car.reward = self.calculateFitness(car, simulation)

    #Check cars
    def isDone(self, simulation):
        done = True

        #Episode continues
        for car in self.population:
            if(not car.isDead):
                car.think(rc=car.calculateRaycasts(simulation.space))
                done = False
        
        return done

        
            



        

    