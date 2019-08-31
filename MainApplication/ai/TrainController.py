from objs.kivyObjs import distXY


class TrainController():
    def __init__(self, simulation):
        self.simulation = simulation
        self.games = 10
        self.game = 0

        #Movement check vars
        self.minMoveDist = 25
        self.lastPos = None
        self.minStepsDelta = 100
        self.initialSteps = 0


        #Training vars
        self.state = None
        self.game_data = []
        self.game_data_packets = []
        self.scores = []
        self.testedCar = None

        #Training speed / Show speed
        self.trainingSpeed = 20
        self.showSpeed = 2

        self.deadCarsKy = []

        self.startTrain()

    #Start training session
    def startTrain(self, *args):
        self.state = 1
        self.simulation.simulationSpeed = self.trainingSpeed
        self.game = 0

        self.simulation.resetLevel()

        if(self.testedCar != None):
            model = self.testedCar.brain
            self.testedCar = self.simulation.addCarAI()  
            self.testedCar.brain = model

        else:
            self.testedCar = self.simulation.addCarAI()   
            self.testedCar.generateRandomBrain() 

        self.initMovementCheck()

    #End training session
    def endTrain(self):
        self.state = 0
        self.simulation.simulationSpeed = self.showSpeed
        return self.testedCar

    #Calculate fitness of a model
    def calculateFitness(self):
        dist = self.testedCar.distToFinish(self.simulation)
        if(dist != 0):
            fitness = fitness = pow(1/(dist),2)
        else:
            fitness = fitness = pow(1/(dist+0.0001),2)
        fitness *= 100000
        return fitness

    #Print packet data
    def printPackets(self, packets):
        for packet in packets:
            print("Score: {}, Data len: {}".format(packet["score"], len(packet["data"])))

    #Unpack packet data 
    def unpack(self, packets):
        observations = []
        actions = []
        for packet in packets:
            game_data = packet["data"]
            for data in game_data:
                observations.append(data[0])
                actions.append(data[1])

        return [observations, actions]

    #Check if testedCar has moved
    def checkMovement(self):
        pos = self.testedCar.body.position
        if(self.lastPos != None):
            if(not(self.minMoveDist < distXY(self.lastPos,pos))):
                self.testedCar.kill()
                print("Did NOT pass Dist: {}".format(distXY(self.lastPos,pos)))
            else:
                print("Did pass Dist: {}".format(distXY(self.lastPos,pos)))
                self.lastPos = pos
                self.initialSteps = self.simulation.space.steps

    #Set default values for movement check
    def initMovementCheck(self):
        self.lastPos = self.testedCar.body.position
        self.initialSteps = self.simulation.space.steps

    #End of the round (Car died timer is up)
    def endOfRound(self):
        self.game += 1
        self.game_data_packets.append({"score":self.calculateFitness(), "data":self.game_data})
        self.game_data = []
        print(self.game)

        #If this was last game
        if(self.game == self.games):
            self.endOfSession()
            
        #Prepare for next game
        else:
            self.initMovementCheck()
            self.testedCar.respawn(self.simulation)

    #End of learning session (All learning games passed)
    def endOfSession(self):
        self.state = 2 #Set to learning
        self.simulation.resetLevel()

        #Sort all result by score
        self.game_data_packets.sort(key=lambda x: x["score"], reverse=True)

        #Best 20%
        bestResults = []
        for index, packet in enumerate(self.game_data_packets):
            if(index+1 > 0.2*len(self.game_data_packets)):
                break
            
            bestResults.append(packet)

        print("Best Result: {}".format(bestResults[0]["score"]))

        #Train on best 20%
        self.testedCar.brain.fit(self.unpack(bestResults))

        self.startTrain()

    #Training loop
    def loop(self):
        if(self.state == 1):
            scaller = self.simulation.canvasWindow.scaller
            posX = (-1*self.testedCar.body.position[0]*scaller)
            posX += self.simulation.canvasWindow.size[0]/2

            posY = (-1*self.testedCar.body.position[1]*scaller)
            posY += self.simulation.canvasWindow.size[1]/2
            self.simulation.canvasWindow.pos = (posX, posY)

            #Movement check
            if(self.simulation.space.steps >= self.initialSteps+self.minStepsDelta):
                self.checkMovement()

            #End of round (Car died or timer is up)
            if(self.testedCar.isDead):
                self.endOfRound()

            #Current test continues --> Did NOT died
            else:
                observation = self.testedCar.calculateRaycasts(self.simulation.space)
                action = self.testedCar.think(observation)

                self.game_data.append([observation, action])