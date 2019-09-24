import keras
import random
import math
import numpy as np
from collections import deque

class DQN():
    def __init__(self, discount=0.95, exploration_min=0.01, exploration_max=1, exploration_decay=0.995, batch_size=20):
        #Set constants
        self.discount = discount
        self.exploration_min = exploration_min
        self.exploration_max = exploration_max
        self.exploration_decay = exploration_decay
        self.batch_size = batch_size

        #Prepare variables
        self.exploration_rate = None #Create it just you know it exists :)
        self.resetExplorationRate()

        #Variable for storing state-action pairs
        self.memory = deque()

        #Temp variables
        self.tempSAPair = None

    #Reset exploration rate
    def resetExplorationRate(self):
        self.exploration_rate = self.exploration_max

    #New run, Prepare vars for new run
    def newRun(self):
        self.tempSAPair = None

    #Choose action based in observation or explore
    def act(self, model, obs, action_space=2):
        if(np.random.random() < self.exploration_rate):
            #Take random action
            return np.random.randint(action_space)

        else:
            #Predict action from AI model
            return np.argmax(model.predict(obs)[0]) #Return only highest predicted index

    #Save state-action pair
    def remember(self, obs, action, obs1, reward):
        self.memory.append((obs, action, obs1, reward))

    def experience_replay(self, model):
        if(len(self.memory) < self.batch_size):
            return

        #Select random memories
        batch = random.sample(self.memory, self.batch_size)

        for obs, action, obs1, reward in batch:
            #Calculate New Update Q-Value
            q_update = reward + self.discount * np.amax(model.predict(obs1)[0])

            #Predict on current value
            q_values = model.predict(obs)

            #Update actual Q-Value
            q_values[0][action] = q_update

            #Fit on calculated Q-Values
            model.fit(obs, q_values, verbose=0)
        
        #Decrease exploration rate
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(self.exploration_min, self.exploration_rate)

