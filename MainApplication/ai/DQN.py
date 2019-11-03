import keras
import random
import math
import numpy as np
import multiprocessing as mp
from collections import deque

#Sequence generator
from ai.SeqGen import SeqGen
from objs.kivyObjs import distXY

class DQN():
    def __init__(self, discount=0.95, exploration_min=0.01, exploration_max=1, exploration_decay=0.995, batch_size=20):
        #Set constants
        self.discount = discount
        self.exploration_min = exploration_min
        self.exploration_max = exploration_max
        self.exploration_decay = exploration_decay
        self.batch_size = batch_size

        #Prepare variables
        self.highestReward = 0
        self.highestRewardedModel = None
        self.deathCount = 0
        self.tempSAPair = None
        self.exploration_rate = None #Create it just you know it exists :)
        self.resetExplorationRate()

        #Variable for storing state-action pairs
        self.memory = deque()
        self.hm_steps = 0

        #Learning object
        self.dqnCar = None

    #Reset exploration rate
    def resetExplorationRate(self):
        self.exploration_rate = self.exploration_max

    #Decreases exploration rate by decay
    def decayExplorationRate(self):
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(self.exploration_min, self.exploration_rate)

    #Respawn object
    def respawnCar(self, simulation):
        #Save best rewarded (reward + model)
        if(self.dqnCar != None):
            self.deathCount += 1
            if(self.dqnCar.reward > self.highestReward):
                self.highestReward = self.dqnCar.reward
                self.highestRewardedModel = self.dqnCar.model

        #Reset level & steps
        simulation.resetLevel()
        self.startSteps = simulation.space.steps

        #If respawn save brain then load it again
        if(self.dqnCar != None):
            self.dqnCar = simulation.addCarAI(self.dqnCar.model)

        #First spawn --> create brain
        else:
            self.dqnCar = simulation.addCarAI()

        #Set camera
        simulation.canvasWindow.selectedCar = self.dqnCar

        #Reset reward when new spawn
        self.dqnCar.reward = 0

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

    #Half Q-Learning
    def fast_experience_replay(self, model, graph):
        if(len(self.memory) < self.batch_size):
            return

        #Select random memories
        batch = random.sample(self.memory, self.batch_size)
        obsToLearn = []
        actionsToLearn = []

        for obs, action, obs1, reward in batch:
            #Q Function : Immediate reward + Future reward
            with graph.as_default():
                q_update = reward + self.discount * np.amax(model.predict(obs1)[0])

                #Predict on current value
                q_values = model.predict(obs)

            #Update actual Q-Value
            q_values[0][action] = q_update

            #Save Q-Values for fitting
            obsToLearn.append(obs[0])
            actionsToLearn.append(q_values[0])
        
        obsToLearn = np.array(obsToLearn)
        actionsToLearn = np.array(actionsToLearn)

        #Fit on calculated Q-Values
        with graph.as_default():
            model.fit(obsToLearn, actionsToLearn, verbose=0)

        #Decrease exploration rate
        self.decayExplorationRate()

    #Calls every step
    def step(self, simulation):
        #Take observation
        obs1 = self.dqnCar.calculateRaycasts(simulation.space)
        action1 = self.act(self.dqnCar.model, obs1, action_space=self.dqnCar.action_space)

        self.dqnCar.think(None, action1)

        #First time-step --> Save obs & action and use them in next time-step
        if(self.tempSAPair == None):
            self.tempSAPair = (obs1, action1)
            self.pos0 = self.dqnCar.body.position
        
        #Every other time-step
        else:
            #Load prev state-actions
            obs = self.tempSAPair[0]
            action = self.tempSAPair[1]

            #Calculate immediate reward
            reward = 1

            #Reward if fast
            pos0 = self.pos0
            pos1 = self.dqnCar.body.position
            self.pos0 = pos1
            vel = distXY(pos0, pos1)
            if(vel >= 7.5):
                reward = 2
            
            #Punish if close to the wall
            for ob in obs[0]:
                if(ob < 0.1):
                    reward = -1/(ob*100)

            #Punish if died
            if(self.dqnCar.isDead):
                reward = -10
            
            #Add reward to overall reward
            self.dqnCar.reward += reward

            #Remember state-action pairs
            self.remember(obs, action, obs1, reward)

            #Experience replay
            self.fast_experience_replay(self.dqnCar.model, graph=simulation.graph)

            #Replace old observation with new observation
            self.tempSAPair = (obs1, action1) 