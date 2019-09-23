import tensorflow as tf
import numpy as np

from statistics import median, mean
from collections import Counter
import random

#AI Framework
from keras.models import Sequential
import keras

class NeuralModel():
    def __init__(self, input_size=3, output_size=2, learningRate=1e-3):
        self.learningRate = learningRate

        #Create sequential model
        self.network = self.createSequentialModel(input_size, output_size)

    #Creates sequential model
    def createSequentialModel(self, input_size, output_size, structure=None):
        #Default model
        if(structure==None):
            #Create model
            model = keras.Sequential([
                keras.layers.Dense(64, activation=tf.nn.relu, input_dim=input_size),
                keras.layers.Dense(128, activation=tf.nn.relu),
                keras.layers.Dense(output_size, activation=tf.nn.softmax)
            ])
        else:
            pass
            #Custom model editing

        #Optimizer
        adam = keras.optimizers.Adam(lr=self.learningRate)

        #Compile model
        model.compile(loss='mean_squared_error', optimizer=adam)

        return model

    #Generate prediction
    def predict(self, data):
        result = self.network.predict(data)
        return result

    def mutateWeights(self, mutationRate=0.1):
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
                        one_dim_weight[i]*=np.random.normal(loc=1,scale=0.5)
                        #one_dim_weight[i] *= np.random.random()

                #reshape them back to the original form
                new_weight_array = one_dim_weight.reshape(save_shape)
                #save them to the weight list for the layer
                new_weights_for_layer.append(new_weight_array)

            #set the new weight list for each layer
            self.network.layers[j].set_weights(new_weights_for_layer)