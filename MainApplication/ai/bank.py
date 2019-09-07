import math
import numpy as np

"""
Function bank for AI



"""


#Calculate fitness of a model
def calculateFitness(car, simulation):
    dist = car.distToFinish(simulation)
    if(dist != 0):
        fitness = fitness = pow(1/(dist),2)
    else:
        fitness = fitness = pow(1/(dist+0.0001),2)
    fitness *= 100000
    return fitness

#Print packet data
def printPackets(packets):
    for packet in packets:
        print("Score: {}, Data len: {}".format(packet["score"], len(packet["data"])))

#Unpack packet data 
def unpack(packets):
    observations = []
    actions = []
    for packet in packets:
        game_data = packet["data"]
        for data in game_data:
            observations.append(data[0])
            actions.append(data[1])

    return [observations, actions]