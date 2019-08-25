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

        network = fully_connected(network, 32, activation='sigmoid')
        #network = dropout(network, 0.8)

        network = fully_connected(network, 64, activation='sigmoid')
        #network = dropout(network, 0.8)

        network = fully_connected(network, 32, activation='sigmoid')

        network = fully_connected(network, 4, activation='sigmoid')
        network = regression(network, optimizer='adam', learning_rate=self.learningRate, loss='categorical_crossentropy', name='targets')

        model = tflearn.DNN(network, tensorboard_verbose=3, tensorboard_dir="D:\\Entertaiment\\Programy\\Python\\NeuralSandbox2\\tmp")

        return model

    def getResult(self, rawdata):
        data = []
        data.append(rawdata)
        result = self.network.predict(data)
        return result

    '''
    def neural_network_model(self, data):
        hidden_1_layer = {"weights": tf.Variable(tf.random_normal([3, self.n_nodes_hl1])),
                        "biases": tf.Variable(tf.random_normal([self.n_nodes_hl1]))}

        hidden_2_layer = {"weights": tf.Variable(tf.random_normal([self.n_nodes_hl1, self.n_nodes_hl2])),
                        "biases": tf.Variable(tf.random_normal([self.n_nodes_hl2]))}

        hidden_3_layer = {"weights": tf.Variable(tf.random_normal([self.n_nodes_hl2, self.n_nodes_hl3])),
                        "biases": tf.Variable(tf.random_normal([self.n_nodes_hl3]))}

        output_layer = {"weights": tf.Variable(tf.random_normal([self.n_nodes_hl3, self.n_classes])),
                        "biases": tf.Variable(tf.random_normal([self.n_classes]))}

        l1 = tf.add(tf.matmul(data, hidden_1_layer["weights"]), hidden_1_layer["biases"])
        l1 = tf.nn.relu(l1)

        l2 = tf.add(tf.matmul(l1, hidden_2_layer["weights"]), hidden_2_layer["biases"])
        l2 = tf.nn.relu(l2)

        l3 = tf.add(tf.matmul(l2, hidden_3_layer["weights"]), hidden_3_layer["biases"])
        l3 = tf.nn.relu(l3)

        output = tf.matmul(l3, output_layer["weights"]) + output_layer["biases"]
        output = tf.nn.softmax(output)

        return output
    '''
