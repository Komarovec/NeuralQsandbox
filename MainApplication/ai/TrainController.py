
class TrainController():
    def __init__(self, simulation):
        self.simulation = simulation
        self.games = 100
        self.game = 0

        self.state =  None
        self.game_data = []
        self.game_data_packets = []
        self.scores = []
        self.testedCar = None

        self.deadCarsKy = []

        self.startTrain()

    def startTrain(self):
        self.state = 1
        self.game = 0
        self.simulation.resetLevel()

        self.testedCar = self.simulation.addPlayer()

    def calculateFitness(self):
        dist = self.testedCar.distToFinish(self.simulation)
        if(dist != 0):
            fitness = fitness = pow(1/(dist),2)
        else:
            fitness = fitness = pow(1/(dist+0.0001),2)
        fitness *= 100000
        return fitness 

    def printPackets(self, packets):
        for packet in packets:
            print("Score: {}, Data len: {}".format(packet["score"], len(packet["data"])))

    def unpack(self, packets):
        observations = []
        actions = []
        for packet in packets:
            game_data = packet["data"]
            for data in game_data:
                observations.append(data[0])
                actions.append(data[1])

        return [observations, actions]

    def loop(self):
        if(self.state == 1):
            #Current tested died
            if(self.testedCar.isDead):
                self.game += 1
                self.game_data_packets.append({"score":self.calculateFitness(), "data":self.game_data})
                self.game_data = []
                #print(self.game)

                #If this was last game
                if(self.game == self.games):
                    self.state = 2
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
                    self.simulation.canvasWindow.stopDrawing()
                    self.testedCar.brain.fit(self.unpack(bestResults))
                    self.state = 1
                    self.game = 0
                    self.simulation.space.add(self.testedCar.body, self.testedCar)
                    self.testedCar.paint(self.simulation.canvasWindow)
                    self.testedCar.respawn(self.simulation)
                    self.simulation.canvasWindow.startDrawing()


                #Prepare for next game
                else:
                    #self.deadCarsKy.append(self.testedCar.ky)
                    #self.simulation.space.remove(self.testedCar)
                    self.testedCar.respawn(self.simulation)

            #Current test continues
            else:
                observation = self.testedCar.calculateRaycasts(self.simulation.space)
                action = self.testedCar.think(observation)

                self.game_data.append([observation, action])

    


