from objs.kivyObjs import distXY
from ai.bank import calculateFitness, printPackets, unpack
from ai.DQN import DQN
from objs.GameObjects import StaticGameObject

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
        self.DQN = DQN()
        self.DQN.dqnCar = self.simulation.addCarAI()   
        self.DQN.dqnCar.model = model
        self.exportModel = model

        self.simulation.canvasWindow.changeGameState("exit")

    #Get neural model from states
    def getNetworkFromCar(self):
        #Return dqnCar if learning via reinforcement learning
        if(self.state == self.LEARNING_STATE and self.learningType == self.REINFORCEMENT_LEARN):
            if(self.DQN.dqnCar != None):
                return self.DQN.dqnCar.model
        
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

        self.DQN.respawnCar(self.simulation)

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
        #Save model first
        self.exportModel = self.getNetworkFromCar()

        self.state = self.IDLE_STATE
        self.simulation.simulationSpeed = self.showSpeed
        self.simulation.removeCars()

    #Handle car collisions
    def handleCollision(self, car, otherObject):
        #If collide object is sensor, dont call for collision
        if(otherObject.sensor):
            return

        if(self.state == self.LEARNING_STATE):
            car.kill(self.simulation.canvasWindow)
        elif(self.state == self.TESTING_STATE):
            car.respawn(self.simulation)
        elif(self.state == self.PLAYING_STATE and otherObject.objectType == StaticGameObject.FINISH):
            car.respawn(self.simulation)

    #End of the Run (Car died or timer is up)
    def endOfRun(self):
        self.game += 1

        if(self.learningType == self.REINFORCEMENT_LEARN):
            #Update all GUI
            self.simulation.canvasWindow.window.stateInfoBar.addPlotPointRight(self.game, self.DQN.dqnCar.reward)
            self.simulation.canvasWindow.window.stateInfoBar.addPlotPointLeft(self.game, self.DQN.exploration_rate)

            #Prepare for next game
            self.DQN.respawnCar(self.simulation)

        elif(self.learningType == self.GENETIC_LEARN):
            pass

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
                    self.DQN.learn(self.simulation)
                    self.endOfRun()

                #Current test continues --> Did NOT died
                else:
                    self.DQN.learn(self.simulation)
            
            #SGA Learning
            elif(self.learningType == self.GENETIC_LEARN):
                pass

            #NEAT Learning
            elif(self.learningType == self.NEAT_LEARN):
                pass

        #Testing model
        elif(self.state == self.TESTING_STATE):
            if(self.testCar != None):
                car = self.testCar
                observation = np.array(car.calculateRaycasts(self.simulation.space))
                car.think(observation)