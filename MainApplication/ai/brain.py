import tensorflow as tf
import numpy as np

n_nodes_hl1 = 8
n_nodes_hl2 = 8
n_nodes_hl3 = 8

n_classes = 2

def neural_network_model(data):
    hidden_1_layer = {"weights": tf.Variable(tf.random_normal([3, n_nodes_hl1])),
                      "biases": tf.Variable(tf.random_normal([n_nodes_hl1]))}

    hidden_2_layer = {"weights": tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      "biases": tf.Variable(tf.random_normal([n_nodes_hl2]))}

    hidden_3_layer = {"weights": tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                      "biases": tf.Variable(tf.random_normal([n_nodes_hl3]))}

    output_layer = {"weights": tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                      "biases": tf.Variable(tf.random_normal([n_classes]))}

    l1 = tf.add(tf.matmul(data, hidden_1_layer["weights"]), hidden_1_layer["biases"])
    l1 = tf.nn.relu(l1)

    l2 = tf.add(tf.matmul(l1, hidden_2_layer["weights"]), hidden_2_layer["biases"])
    l2 = tf.nn.relu(l2)

    l3 = tf.add(tf.matmul(l2, hidden_3_layer["weights"]), hidden_3_layer["biases"])
    l3 = tf.nn.relu(l3)

    output = tf.matmul(l3, output_layer["weights"]) + output_layer["biases"]

    return output

def getModel():
    x = tf.compat.v1.placeholder("float", [None, 3])
    prediction = neural_network_model(x)
    return prediction

def getRandomResult(rawdata, prediction):
    data = []
    for _ in range(8):
        data.append(rawdata)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        sess.run(prediction, {x: data})

