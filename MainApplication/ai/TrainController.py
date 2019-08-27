
class TrainController():
    def __init__(self, simulation):
        self.simulation = simulation
        self.games = 10
        self.game = 0

        self.state =  None
        self.game_data = []        
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

    def 

    def loop(self):
        if(self.state == 1):
            #Current tested died
            if(self.testedCar.isDead):
                self.scores.append(self.calculateFitness())
                print(self.game)

                #If this was last game
                if(self.game == self.games):
                    self.state = 2
                    self.simulation.resetLevel()
                    print("Game data len: {}; Scores len: {}".format(len(self.game_data), len(self.scores)))
                    print(self.scores)
                    #Traininng session ended

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

    


