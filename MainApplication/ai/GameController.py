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

    def __init__(self, simulation):
        self.simulation = simulation
        self.bestPercentage = 0.2
        self.game = 0

        # Skip step
        self.memoryStep = 0;
        self.memoryAction = None;

        # Training vars
        self.learningType = self.REINFORCEMENT_LEARN
        self.state = self.IDLE_STATE
        self.stepLimit = 5000
        self.startSteps = 0

        # Learning objects
        self.DQN = DQN()

        # Cars
        self.testCar = None

        # Network to Export
        self.exportModel = None

        # Training speed / Show speed
        self.trainingSpeed = 8
        self.showSpeed = 2

    # Get neural model
    def getNetwork(self):
        model = self.getNetworkFromCar()
        if(model != None):
            return model
        else:
            return self.exportModel

    # Set neural network
    def setNetwork(self, model):
        if(model == None):
            return

        self.resetNetwork()
        self.exportModel = model
        self.simulation.gameController.updateGUI()

    # New network
    def resetNetwork(self):
        config = App.get_running_app().config

        # Training vars
        learn_type = config.get('AI', 'learn_type')
        if(learn_type == "DQN"):
            self.learningType = self.REINFORCEMENT_LEARN
        elif(learn_type == "SGA"):
            self.learningType = self.GENETIC_LEARN

        # Reset all learning object and values
        self.DQN = DQN(float(config.get('DQN','dqn_discount_factor')), float(config.get('DQN','dqn_exploration_min')),
                    float(config.get('DQN','dqn_exploration_max')), float(config.get('DQN','dqn_exploration_decay')), 
                    int(config.get('DQN','dqn_batch_size')))

        self.exportModel = None
        self.game = 0

        # Reset graphics
        self.updateGUI()

        # Start idling
        self.simulation.canvasWindow.changeGameState("exit")

    # Get neural model from states
    def getNetworkFromCar(self):
        # Return car if learning
        if(self.state == self.LEARNING_STATE):
            # via Reinforcement learn
            if(self.learningType == self.REINFORCEMENT_LEARN):
                if(self.DQN.dqnCar != None):
                    return self.DQN.dqnCar.model
        
        # Return testCar if testing
        elif(self.state == self.TESTING_STATE):
            if(self.testCar != None):
                return self.testCar.model

        return None


    # Changes state to train
    def startTrain(self, *args):
        # Pause physics thread
        self.simulation.endPhysicsThread()

        # Prepare game vars
        self.simulation.simulationSpeed = self.trainingSpeed
        self.game = 0

        # Prepare DQN
        if(self.learningType == self.REINFORCEMENT_LEARN):
            self.DQN.respawnCar(self.simulation)

        # Change state last --> Threaded
        self.state = self.LEARNING_STATE

        # Reset start steps
        self.startSteps = self.simulation.space.steps

        # Resume physics thread
        self.simulation.startPhysicsThread()

    # Changes state to testing
    def startTest(self):
        # Pause physics thread
        self.simulation.endPhysicsThread()

        # Load model first
        model = self.exportModel

        # Prepare Controller
        self.testCar = None

        # Prepare enviroment simulation
        self.simulation.simulationSpeed = self.showSpeed
        self.simulation.removeCars()
        
        # Copy model or create new
        if(model != None):
            # Copy brain
            car = self.simulation.addCarAI(model)
        else:
            # Generate random
            car = self.simulation.addCarAI()

        self.testCar = car

        # Set camera
        self.simulation.canvasWindow.selectedCar = car

        # Change state last --> Threaded
        self.state = self.TESTING_STATE

        # Resume physics thread
        self.simulation.startPhysicsThread()

    # Changes state to free play
    def startFreePlay(self):
        # Pause physics thread
        self.simulation.endPhysicsThread()

        car = self.simulation.addPlayer()

        # Set camera
        self.simulation.canvasWindow.selectedCar = car

        # Change state last --> Threaded
        self.state = self.PLAYING_STATE

        # Resume physics thread
        self.simulation.startPhysicsThread()

    # Changes state to IDLE
    def startIdle(self):
        # Pause physics thread
        self.simulation.endPhysicsThread()

        # Save model first, but do not save model when playing --> nothing to save
        if(self.state != self.PLAYING_STATE):
            self.exportModel = self.getNetworkFromCar()

        self.state = self.IDLE_STATE
        self.simulation.simulationSpeed = self.showSpeed
        self.simulation.removeCars()

        # Resume physics thread
        self.simulation.startPhysicsThread()

    # Handle car collisions
    def handleCollision(self, car, otherObject):
        # If collide object is sensor, dont call for collision
        if(otherObject.sensor):
            return

        # Learning
        if(self.state == self.LEARNING_STATE):
            car.kill(self.simulation.canvasWindow)
        
        # Testing
        elif(self.state == self.TESTING_STATE):
            car.respawn(self.simulation)
        
        # Playing
        elif(self.state == self.PLAYING_STATE and otherObject.objectType == StaticGameObject.FINISH):
            car.respawn(self.simulation)

    # GUI Update --> call at the end of the Run
    def updateGUI(self):
        guiObject = self.simulation.canvasWindow.window.stateInfoBar

        # Update all GUI
        if(self.learningType == self.REINFORCEMENT_LEARN):
            # Change graph names
            guiObject.changeGraphLabel(guiObject.graph1, "Deaths", "Reward")
            guiObject.changeGraphLabel(guiObject.graph2, "Deaths", "Exploration rate")

            # Add point to graphs
            if(self.DQN.dqnCar != None):
                guiObject.addPlotPointRight(self.DQN.deathCount, self.DQN.dqnCar.reward)
                guiObject.addPlotPointLeft(self.DQN.deathCount, (self.DQN.exploration_rate*100))

            # Change values overall
            guiObject.setValue1("Learning type", "DQN")
            guiObject.setValue2("Memories", len(self.DQN.memory))

            # Current run
            guiObject.setValue3("Exploration rate", round((self.DQN.exploration_rate*100),2))
            guiObject.setValue4("Max reward", round(self.DQN.highestReward,2))

        else: # Testing stage
            pass


    # End of the Run (Car died or timer is up)
    def endOfRun(self):
        self.game += 1

        # Update GUI
        self.updateGUI()

        if(self.learningType == self.REINFORCEMENT_LEARN):
            # Prepare for next game
            self.DQN.respawnCar(self.simulation)

        # Reset timer
        self.startSteps = self.simulation.space.steps

    # Training loop --> run every game
    def loop(self):
        # Training model
        if(self.state == self.LEARNING_STATE):
            if(self.DQN.dqnCar == None): return

            # If time ran out end the round without punish
            if((self.simulation.space.steps-self.startSteps) > self.stepLimit):
                self.endOfRun()

            # DQN Learning
            elif(self.learningType == self.REINFORCEMENT_LEARN):
                # If car died, punish it and then end the round
                if(self.DQN.dqnCar.isDead):
                    self.DQN.step(self.simulation)
                    self.endOfRun()

                # Current test continues --> Did NOT died
                else:
                    if(self.memoryStep == 0):
                        self.DQN.step(self.simulation)
                    else:
                        self.DQN.dqnCar.takeLastAction()

        # Testing model
        elif(self.state == self.TESTING_STATE):
            if(self.testCar != None):
                car = self.testCar

                if(self.memoryStep == 0):
                    observation = np.array(car.calculateRaycasts(self.simulation.space))
                    car.takeAction(dist=observation, graph=self.simulation.graph)
                else:
                    car.takeLastAction()

        # Reset memory step
        if(self.state != self.PLAYING_STATE):
            self.memoryStep += 1
            if(self.memoryStep >= 3):
                self.memoryStep = 0;