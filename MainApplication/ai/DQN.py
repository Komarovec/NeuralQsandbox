import keras
import random
import math
import numpy as np
import multiprocessing as mp
from collections import deque

#Sequence generator
from ai.SeqGen import SeqGen

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
        self.hm_steps = 0

        #Temp variables
        self.tempSAPair = None

    #Reset exploration rate
    def resetExplorationRate(self):
        self.exploration_rate = self.exploration_max

    #Decreases exploration rate by decay
    def decayExplorationRate(self):
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(self.exploration_min, self.exploration_rate)

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

    #Full Q-Learning -Extremely slow
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
        self.decayExplorationRate()

    #Half Q-Learning
    def fast_experience_replay(self, model):
        if(len(self.memory) < self.batch_size):
            return

        #Select random memories
        batch = random.sample(self.memory, self.batch_size)

        obsToLearn = []
        actionsToLearn = []

        for obs, action, obs1, reward in batch:
            #Calculate New Update Q-Value
            q_update = reward + self.discount * np.amax(model.predict(obs1)[0])

            #Predict on current value
            q_values = model.predict(obs)

            #Update actual Q-Value
            q_values[0][action] = q_update

            #Fit on calculated Q-Values
            obsToLearn.append(obs[0])
            actionsToLearn.append(q_values[0])
        
        obsToLearn = np.array(obsToLearn)
        actionsToLearn = np.array(actionsToLearn)

        model.fit(obsToLearn, actionsToLearn, verbose=0)
        
        #Decrease exploration rate
        self.decayExplorationRate()

    #Q-Learning after run
    def late_experience_replay(self, model):
        if(len(self.memory) < self.batch_size):
            return

        batch = []
        for _ in range(self.hm_steps):
            #Select random memories
            batch.extend(random.sample(self.memory, self.batch_size))

        self.hm_steps = 0

        obsToLearn = []
        actionsToLearn = []

        for obs, action, obs1, reward in batch:
            #Calculate New Update Q-Value
            q_update = reward + self.discount * np.amax(model.predict(obs1)[0])

            #Predict on current value
            q_values = model.predict(obs)

            #Update actual Q-Value
            q_values[0][action] = q_update

            #Fit on calculated Q-Values
            obsToLearn.append(obs[0])
            actionsToLearn.append(q_values[0])
        
        obsToLearn = np.array(obsToLearn)
        actionsToLearn = np.array(actionsToLearn)

        workers = mp.cpu_count()

        batch_gen_size = round(len(obsToLearn)/workers)

        print("batch size: {}".format(batch_gen_size))

        model.fit_generator(generator=SeqGen(obsToLearn, actionsToLearn, batch_size=batch_gen_size), epochs=1, verbose=0, workers=workers)