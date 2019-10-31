from objs.kivyObjs import distXY
from ai.DQN import DQN
from ai.SGA import SGA
from objs.GameObjects import StaticGameObject

from kivy.app import App

import numpy as np
import math

class GameController():
    IDLE_STATE = 0
    LEARNING_STATE = 1
    TESTING_STATE = 2
    PLAYING_STATE = 3

    REINFORCEMENT_LEARN = "reinforcement"
    GENETIC_LEARN = "genetic"
    NEAT_LEARN = "neat"

    def __init__(self, simulation):
        self.simulation = simulation
        self.bestPercentage = 0.2
        self.game = 0

        #Training vars
        self.learningType = self.REINFORCEMENT_LEARN
        self.state = self.IDLE_STATE
        self.stepLimit = 5000
        self.startSteps = 0

        #Learning objects
        self.DQN = DQN()
        self.SGA = SGA()

        #Cars
        self.testCar = None

        #Network to Export
        self.exportModel = None

        #Training speed / Show speed
        self.trainingSpeed = 8
        self.showSpeed = 2

    #Get neural model
    def getNetwork(self):
        model = self.getNetworkFromCar()
        if(model != None):
            return model
        else:
            return self.exportModel

    #Set neural network
    def setNetwork(self, model):
        self.resetNetwork()
        self.exportModel = model

    #New network
    def resetNetwork(self):
        config = App.get_running_app().config

        #Training vars
        learn_type = config.get('AI', 'learn_type')
        if(learn_type == "DQN"):
            self.learningType = self.REINFORCEMENT_LEARN
        elif(learn_type == "SGA"):
            self.learningType = self.GENETIC_LEARN

        #Reset all learning object and values
        self.DQN = DQN(float(config.get('DQN','dqn_discount_factor')), float(config.get('DQN','dqn_exploration_min')),
                    float(config.get('DQN','dqn_exploration_max')), float(config.get('DQN','dqn_exploration_decay')), 
                    int(config.get('DQN','dqn_batch_size')))

        self.SGA = SGA(int(config.get('SGA','sga_population_size')), float(config.get('SGA','sga_mutation_rate')))
        self.exportModel = None
        self.game = 0

        #Start idling
        self.simulation.canvasWindow.changeGameState("exit")

    #Get neural model from states
    def getNetworkFromCar(self):
        #Return car if learning
        if(self.state == self.LEARNING_STATE):
            #via Reinforcement learn
            if(self.learningType == self.REINFORCEMENT_LEARN):
                if(self.DQN.dqnCar != None):
                    return self.DQN.dqnCar.model

            #via Genetic learn
            elif(self.learningType == self.GENETIC_LEARN):
                if(self.SGA.highestRewardedModel != None):
                    return self.SGA.highestRewardedModel.model
        
        #Return testCar if testing
        elif(self.state == self.TESTING_STATE):
            if(self.testCar != None):
                return self.testCar.model

        return None


    #Changes state to train
    def startTrain(self, *args):
        #Prepare game vars
        self.state = self.LEARNING_STATE
        self.simulation.simulationSpeed = self.trainingSpeed
        self.game = 0

        #Prepare DQN
        if(self.learningType == self.REINFORCEMENT_LEARN):
            self.DQN.respawnCar(self.simulation)
        
        #Prepare SGA
        elif(self.learningType == self.GENETIC_LEARN):
            #If no population generate it
            if(self.SGA.population == []):
                self.SGA.randomPopulation(self.simulation)
            else:
                self.simulation.loadCars(self.SGA.population)

        #Prepare NEAT
        elif(self.learningType == self.NEAT_LEARN):
            pass

    #Changes state to testing
    def startTest(self):
        #Load model first
        model = self.exportModel

        #Prepare Controller
        self.testCar = None
        self.state = self.TESTING_STATE

        #Prepare enviroment simulation
        self.simulation.simulationSpeed = self.showSpeed
        self.simulation.removeCars()
        
        #Copy model or create new
        if(model != None):
            #Copy brain
            car = self.simulation.addCarAI(model)
        else:
            #Generate random
            car = self.simulation.addCarAI()

        self.testCar = car

        #Set camera
        self.simulation.canvasWindow.selectedCar = car

    #Changes state to free play
    def startFreePlay(self):
        self.state = self.PLAYING_STATE
        car = self.simulation.addPlayer()

        #Set camera
        self.simulation.canvasWindow.selectedCar = car

    #Changes state to IDLE
    def startIdle(self):
        #Save model first, but do not save model when playing --> nothing to save
        if(self.state != self.PLAYING_STATE):
            self.exportModel = self.getNetworkFromCar()

        self.state = self.IDLE_STATE
        self.simulation.simulationSpeed = self.showSpeed
        self.simulation.removeCars()

    #Handle car collisions
    def handleCollision(self, car, otherObject):
        #If collide object is sensor, dont call for collision
        if(otherObject.sensor):
            return

        #Learning
        if(self.state == self.LEARNING_STATE):
            car.kill(self.simulation.canvasWindow)

            #When learning by neuroevolution calculate fitness on death
            if(self.learningType == self.GENETIC_LEARN):
                self.SGA.carDied(car, self.simulation)
        
        #Testing
        elif(self.state == self.TESTING_STATE):
            car.respawn(self.simulation)
        
        #Playing
        elif(self.state == self.PLAYING_STATE and otherObject.objectType == StaticGameObject.FINISH):
            car.respawn(self.simulation)

    #GUI Update --> call at the end of the Run
    def updateGUI(self):
        guiObject = self.simulation.canvasWindow.window.stateInfoBar

        #Update all GUI
        if(self.learningType == self.REINFORCEMENT_LEARN):
            #Add point to graphs
            guiObject.addPlotPointRight(self.DQN.deathCount, self.DQN.dqnCar.reward)
            guiObject.addPlotPointLeft(self.DQN.deathCount, (self.DQN.exploration_rate*100))

            #Change values overall
            guiObject.setValue1("Learning type", "DQN")
            guiObject.setValue2("Memories", len(self.DQN.memory))

            #Current run
            guiObject.setValue3("Exploration rate", (self.DQN.exploration_rate*100))
            guiObject.setValue4("Max reward", self.DQN.highestReward)

        elif(self.learningType == self.GENETIC_LEARN):
            #Add point to graphs
            guiObject.addPlotPointRight(self.SGA.generation, self.SGA.highestReward)
            guiObject.addPlotPointLeft(self.SGA.generation, self.SGA.averageReward)

            #Change values overall
            guiObject.setValue1("Learning type", "SGA")
            guiObject.setValue2("Generation", self.SGA.generation)

            #Current run
            guiObject.setValue3("Average reward", self.SGA.averageReward)
            guiObject.setValue4("Max reward", self.SGA.highestReward)

        elif(self.learningType == self.NEAT_LEARN):
            pass

    #End of the Run (Car died or timer is up)
    def endOfRun(self):
        self.game += 1

        #Update GUI
        self.updateGUI()

        if(self.learningType == self.REINFORCEMENT_LEARN):
            #Prepare for next game
            self.DQN.respawnCar(self.simulation)

        elif(self.learningType == self.GENETIC_LEARN):
            #Generate new population
            self.SGA.newPopulation(self.simulation)

        elif(self.learningType == self.NEAT_LEARN):
            pass

        #Reset timer
        self.startSteps = self.simulation.space.steps

    #Training loop --> run every game
    def loop(self):
        #Training model
        if(self.state == self.LEARNING_STATE):
            #If time ran out end the round without punish
            if((self.simulation.space.steps-self.startSteps) > self.stepLimit):
                self.endOfRun()

            #DQN Learning
            elif(self.learningType == self.REINFORCEMENT_LEARN):
                #If car died, punish it and then end the round
                if(self.DQN.dqnCar.isDead):
                    self.DQN.step(self.simulation)
                    self.endOfRun()

                #Current test continues --> Did NOT died
                else:
                    self.DQN.step(self.simulation)
            
            #SGA Learning
            elif(self.learningType == self.GENETIC_LEARN):
                if(self.SGA.isDone(self.simulation)):
                    self.endOfRun()

            #NEAT Learning
            elif(self.learningType == self.NEAT_LEARN):
                pass

        #Testing model
        elif(self.state == self.TESTING_STATE):
            if(self.testCar != None):
                car = self.testCar
                observation = np.array(car.calculateRaycasts(self.simulation.space))
                car.think(observation, graph=self.simulation.graph)