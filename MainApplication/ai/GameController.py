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
    EVOLUTION_LEARN = "evolution"

    def __init__(self, simulation):
        self.simulation = simulation
        self.bestPercentage = 0.2
        self.game = 0

        #Movement check vars
        self.minMoveDist = 200
        self.lastPos = None
        self.minStepsDelta = 100
        self.initialSteps = 0

        #Training vars
        self.learningType = self.REINFORCEMENT_LEARN
        self.state = self.IDLE_STATE
        self.stepLimit = 5000
        self.startSteps = 0
        self.game_data = []
        self.game_data_packets = []
        self.scores = []

        #Learning objects
        self.DQN = DQN()

        #One-Gen statistical values
        self.bestGenFit = 0

        #Whole statistical values
        self.bestFit = 0

        #Cars
        self.testedCar = None
        self.cars = []

        #Training speed / Show speed
        self.trainingSpeed = 2
        self.showSpeed = 2

        self.deadCarsKy = []

    #Start training Episode
    def startTrain(self, *args):
        #Prepare game vars
        self.state = self.LEARNING_STATE
        self.simulation.simulationSpeed = self.trainingSpeed
        self.game = 0

        #DQN Preparation
        self.DQN.newRun()

        #Spawn car
        self.respawnCar()

    #Start testing learned model
    def startTest(self):
        #Prepare Controller
        self.cars = []
        self.state = self.TESTING_STATE

        #Prepare enviroment simulation
        self.simulation.simulationSpeed = self.showSpeed
        self.simulation.removeCars()

        car = self.simulation.addCarAI()
        
        if(self.testedCar != None):
            car.brain = self.testedCar.brain
        else:
            car.generateRandomBrain()

        self.cars.append(car)

        #Set camera
        self.simulation.canvasWindow.selectedCar = car

    #Free play
    def startFreePlay(self):
        self.state = self.PLAYING_STATE
        car = self.simulation.addPlayer()

        #Set camera
        self.simulation.canvasWindow.selectedCar = car

    #End training EpisodeY
    def endTrain(self):
        self.state = self.IDLE_STATE
        self.simulation.simulationSpeed = self.showSpeed
        self.simulation.removeCars()
        return self.testedCar

    #Stop anything 
    def forceStop(self):
        self.state = self.IDLE_STATE
        self.simulation.simulationSpeed = self.showSpeed
        self.simulation.removeCars()

    #Respawn controller ONLY FOR LEARNING
    def respawnCar(self):
        #Reset level & steps
        self.simulation.resetLevel()
        self.startSteps = self.simulation.space.steps

        #If respawn save brain then load it again
        if(self.testedCar != None):
            model = self.testedCar.brain
            self.testedCar = self.simulation.addCarAI()  
            self.testedCar.brain = model

        #First spawn --> create brain
        else:
            self.testedCar = self.simulation.addCarAI()   
            self.testedCar.generateRandomBrain()

        #Set camera
        self.simulation.canvasWindow.selectedCar = self.testedCar 

        self.initMovementCheck()

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

    #Check if testedCar has moved
    def checkMovement(self):
        pos = self.testedCar.body.position
        if(self.lastPos != None):
            #If did not pass 
            if(not(self.minMoveDist < distXY(self.lastPos,pos))):
                self.testedCar.kill(self.simulation.canvasWindow)
                #print("Did NOT pass Dist: {}".format(distXY(self.lastPos,pos)))
            
            #If passed
            else:
                #print("Did pass Dist: {}".format(distXY(self.lastPos,pos)))
                self.lastPos = pos
                self.initialSteps = self.simulation.space.steps

    #Set default values for movement check
    def initMovementCheck(self):
        self.lastPos = self.testedCar.body.position
        self.initialSteps = self.simulation.space.steps

    #End of the Run (Car died or timer is up)
    def endOfRun(self):
        self.game += 1
        
        #Update all GUI
        self.simulation.canvasWindow.window.stateInfoBar.addPlotPointRight(self.game, self.testedCar.reward)

        #Reset reward counting
        self.testedCar.reward = 0

        #Prepare for next game
        self.respawnCar()

    def learnModel(self):
        if(self.learningType == self.REINFORCEMENT_LEARN):
            #Take observation
            obs1 = self.testedCar.calculateRaycasts(self.simulation.space)
            action1 = self.DQN.act(self.testedCar.brain.network, obs1, action_space=self.testedCar.action_space)

            self.testedCar.think(None, action1)

            #First time-step --> Save obs & action and use them in next time-step
            if(self.DQN.tempSAPair == None):
                self.DQN.tempSAPair = (obs1, action1)
                self.pos0 = self.testedCar.body.position
            
            #Every other ts
            else:
                #Load prev state-actions
                obs = self.DQN.tempSAPair[0]
                action = self.DQN.tempSAPair[1]

                #Calculate immediate reward
                reward = 0

                #Reward if fast
                pos0 = self.pos0
                pos1 = self.testedCar.body.position
                self.pos0 = pos1
                vel = distXY(pos0, pos1)
                if(vel > 7.5):
                    reward = 1

                #Punish if died
                if(self.testedCar.isDead):
                    reward = -1
                
                #Punish if close to the wall
                for ob in obs[0]:
                    if(ob < 0.1):
                        reward = -1
                
                print("Reward: {}".format(reward))
                self.testedCar.reward += reward

                #Remember state-action pairs
                self.DQN.remember(obs, action, obs1, reward)

                #Experience replay
                self.DQN.experience_replay(self.testedCar.brain.network)

                #Replace old observation with new observation
                self.DQN.tempSAPair = (obs1, action1)

    #Training loop
    def loop(self):
        #Training model
        if(self.state == self.LEARNING_STATE):
            #Movement check
            if(self.simulation.space.steps >= self.initialSteps+self.minStepsDelta):
                self.checkMovement()

            #Test if time ran out
            if((self.simulation.space.steps-self.startSteps) > self.stepLimit):
                self.testedCar.kill(self.simulation.canvasWindow)

            #End of Run (Car died or timer is up)
            if(self.testedCar.isDead):
                self.learnModel()
                self.endOfRun()

            #Current test continues --> Did NOT died
            else:
                #Perform action from observation and learning
                self.learnModel()

        #Testing model
        elif(self.state == self.TESTING_STATE):
            if(self.cars != []):
                car = self.cars[0]
                observation = np.array(car.calculateRaycasts(self.simulation.space))
                car.think(observation)