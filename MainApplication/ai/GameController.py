from objs.kivyObjs import distXY
from ai.bank import calculateFitness, printPackets, unpack
from objs.GameObjects import StaticGameObject

import numpy as np
import math

class GameController():
    IDLE_STATE = 0
    LEARNING_STATE = 1
    TESTING_STATE = 2
    PLAYING_STATE = 3

    def __init__(self, simulation):
        self.simulation = simulation
        self.games = 100
        self.bestPercentage = 0.2
        self.game = 0

        #Movement check vars
        self.minMoveDist = 25
        self.lastPos = None
        self.minStepsDelta = 100
        self.initialSteps = 0

        #Training vars
        self.state = self.IDLE_STATE
        self.stepLimit = 5000
        self.startSteps = 0
        self.game_data = []
        self.game_data_packets = []
        self.scores = []

        #One-Gen statistical values
        self.bestGenFit = 0

        #Whole statistical values
        self.bestFit = 0

        #Cars
        self.testedCar = None
        self.cars = []

        #Training speed / Show speed
        self.trainingSpeed = 100
        self.showSpeed = 2

        self.deadCarsKy = []

    #Start training session
    def startTrain(self, *args):
        self.state = self.LEARNING_STATE
        self.simulation.simulationSpeed = self.trainingSpeed
        self.game = 0

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

    #Free play
    def startFreePlay(self):
        self.state = self.PLAYING_STATE
        car = self.simulation.addPlayer()

    #End training sessionY
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

    #Respawn/Spawn car and keep brain if possible
    def respawnCar(self):
        self.simulation.resetLevel()
        self.startSteps = self.simulation.space.steps

        if(self.testedCar != None):
            model = self.testedCar.brain
            self.testedCar = self.simulation.addCarAI()  
            self.testedCar.brain = model

        else:
            self.testedCar = self.simulation.addCarAI()   
            self.testedCar.generateRandomBrain() 

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

    #End of the round (Car died or timer is up)
    def endOfRound(self):
        self.game += 1

        #Calculate fitness and pack collected data
        score = calculateFitness(self.testedCar, self.simulation)
        self.game_data_packets.append({"score":score, "data":self.game_data})
        self.game_data = []
        
        #Update all GUI
        self.simulation.canvasWindow.window.stateInfoBar.setGameVal(self.game)
        self.simulation.canvasWindow.window.stateInfoBar.addGenGraphPoint(self.game, score)
        if(score > self.bestGenFit):
            self.bestGenFit = score
            self.simulation.canvasWindow.window.stateInfoBar.setBestGenFit(round(score,2))

        #If this was last game
        if(self.game == self.games):
            self.endOfSession()
            
        #Prepare for next game
        else:
            self.respawnCar()
            self.testedCar.brain.mutateWeights()

    #End of learning session (All learning games passed)
    def endOfSession(self):
        self.state = 2 #Set to learning
        self.simulation.resetLevel()

        #Sort all result by score
        self.game_data_packets.sort(key=lambda x: x["score"], reverse=True)

        #Best 20%
        bestResults = []
        for index, packet in enumerate(self.game_data_packets):
            #Drop everything below 20%
            if(index+1 > self.bestPercentage*len(self.game_data_packets)):
                break
            
            bestResults.append(packet)

        print("Best Result: {}".format(bestResults[0]["score"]))

        #Train on best 20%
        self.testedCar.brain.fit(unpack(bestResults))

        self.game_data_packets = []
        self.startTrain()

        #Update GUI
        self.simulation.canvasWindow.window.stateInfoBar.setGeneration(self.testedCar.brain.generation)
        self.simulation.canvasWindow.window.stateInfoBar.addOverallGraphPoint(self.testedCar.brain.generation, self.bestGenFit)
        if(self.bestGenFit > self.bestFit):
            self.bestFit = self.bestGenFit
            self.simulation.canvasWindow.window.stateInfoBar.setBestFit(round(self.bestGenFit,2))
        
        self.bestGenFit = 0 #Reset Gen fit

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

            #End of round (Car died or timer is up)
            if(self.testedCar.isDead):
                self.endOfRound()

            #Current test continues --> Did NOT died
            else:
                observation = np.array(self.testedCar.calculateRaycasts(self.simulation.space))

                #print("Gen: {}".format(self.testedCar.brain.generation))
                if(self.testedCar.brain.generation == 0):
                    action = self.testedCar.think(observation, random=True)
                else:
                    action = self.testedCar.think(observation)

                action = np.array(action)

                self.game_data.append([observation, action])

        #Testing model
        elif(self.state == self.TESTING_STATE):
            if(self.cars != []):
                car = self.cars[0]
                observation = np.array(car.calculateRaycasts(self.simulation.space))
                car.think(observation)