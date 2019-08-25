


class TrainController():
    def __init__(self, simulation):
        self.simulation = simulation
        self.games = 10

        self.state =  None
        self.game_data = []        
        self.scores = []
        self.testedCar = None

        self.startTrain()

    def startTrain(self):
        self.state = 1
        self.simulation.resetLevel()

        self.testedCar = self.simulation.addPlayer()

    def loop(self):
        if(self.testedCar.isDead):
            pass
            #print(self.game_data)
        else:
            observation = self.testedCar.calculateRaycasts(self.simulation.space)
            action = self.testedCar.think(observation)
            
            self.game_data.append([observation, action])

    #Dokoncit ucici se smyčku
    


