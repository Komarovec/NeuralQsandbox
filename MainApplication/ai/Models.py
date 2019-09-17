import tensorflow as tf
import numpy as np

from statistics import median, mean
from collections import Counter
import random

#AI Framework
from keras.models import Sequential
import keras

class NeuralModel():
    def __init__(self, input_size=3):
        self.generation = 0
        self.learningRate = 1e-3
        self.epochs = 10
        self.mutationRate = 0.05

        #Create sequential model
        self.network = self.createSequentialModel(input_size)

    def createSequentialModel(self, input_size):
        #Create model
        model = keras.Sequential([
            keras.layers.Dense(4, activation=tf.nn.relu, input_dim=input_size),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(8, activation=tf.nn.relu),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(2, activation=tf.nn.softmax)
        ])

        #Optimizer
        adam = keras.optimizers.Adam(lr=self.learningRate, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)

        #Compile model
        model.compile(loss='mean_squared_error', optimizer='adam',
                    metrics=['accuracy'])

        return model

    def predict(self, rawdata):
        data = np.array(rawdata)
        data = np.array([data])

        result = self.network.predict(data)

        return result

    def mutateWeights(self, mutationRate=None):
        #If not set by user use default
        if(mutationRate == None):
            mutationRate = self.mutationRate

        #first itterate through the layers
        for j, layer in enumerate(self.network.layers):
            new_weights_for_layer = []
            #each layer has 2 matrizes, one for connection weights and one for biases
            #then itterate though each matrix

            for weight_array in layer.get_weights():
                #save their shape
                save_shape = weight_array.shape
                #reshape them to one dimension
                one_dim_weight = weight_array.reshape(-1)

                for i, weight in enumerate(one_dim_weight):
                    #mutate them like i want
                    if(np.random.random() <= mutationRate):
                        #maybe dont use a complete new weigh, but rather just change it a bit
                        one_dim_weight[i]*=np.random.normal(loc=1,scale=0.05)
                        #one_dim_weight[i] *= np.random.random()

                #reshape them back to the original form
                new_weight_array = one_dim_weight.reshape(save_shape)
                #save them to the weight list for the layer
                new_weights_for_layer.append(new_weight_array)

            #set the new weight list for each layer
            self.network.layers[j].set_weights(new_weights_for_layer)

    def fit(self, data):
        X = np.array(data[0])
        Y = np.array(data[1])

        self.generation += 1
        self.network.fit(X, Y, epochs=self.epochs, batch_size=32)