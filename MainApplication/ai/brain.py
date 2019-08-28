import tensorflow as tf
import numpy as np

import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import median, mean
from collections import Counter

class Brain():
    def __init__(self, input_size=3):
        self.learningRate = 1e-3
        self.network = self.neural_network_model(input_size)

    def neural_network_model(self, input_size):
        network = input_data(shape=[None,input_size], name='input')

        network = fully_connected(network, 32, activation='relu')
        #network = dropout(network, 0.8)

        network = fully_connected(network, 64, activation='relu')
        #network = dropout(network, 0.8)

        network = fully_connected(network, 32, activation='relu')

        network = fully_connected(network, 4, activation='softmax')
        network = regression(network, optimizer='adam', learning_rate=self.learningRate, loss='categorical_crossentropy', name='targets')

        model = tflearn.DNN(network)

        return model

    def fit(self, data):
        X = data[0]
        Y = data[1]
        self.network.fit({'input': X}, {'targets': Y}, n_epoch=5, show_metric=True, run_id='openai_learning')

    def getResult(self, rawdata):
        data = []
        data.append(rawdata)
        #data = np.array(data)

        result = self.network.predict(data)

        return result