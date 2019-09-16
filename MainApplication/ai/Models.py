import tensorflow as tf
import numpy as np

from statistics import median, mean
from collections import Counter

#AI Framework
from keras.models import Sequential
import keras

class NeuralModel():
    def __init__(self, input_size=3):
        self.generation = 0
        self.learningRate = 1e-3
        self.epochs = 10

        #Create sequential model
        self.network = self.createSequentialModel(input_size)

    def createSequentialModel(self, input_size):
        #Create model
        model = keras.Sequential([
            keras.layers.Dense(64, activation=tf.nn.relu, input_dim=input_size),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(256, activation=tf.nn.relu),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(64, activation=tf.nn.relu),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(2, activation=tf.nn.softmax)
        ])

        #Optimizer
        adam = keras.optimizers.Adam(lr=self.learningRate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)

        #Compile model
        model.compile(optimizer='adam', 
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])

        return model

    def predict(self, rawdata):
        data = np.array(rawdata)
        data = np.array([data])

        result = self.network.predict(data)

        return result

    def fit(self, data):
        X = np.array(data[0])
        Y = np.array(data[1])

        self.generation += 1
        self.network.fit(X, Y, epochs=self.epochs, batch_size=32)