# AI Framework
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

import tensorflow as tf

DEFAULT_STRUCTURE = [["dense", {"units":64, "activation":"relu"}],["dense", {"units":128, "activation":"relu"}],["dense", {"units":64, "activation":"relu"}]]

# Creates sequential model
def SequentialModel(input_size, output_size, learningRate, structure=None):
    print("creating new model")

    graph = tf.get_default_graph()

    # Default model
    with graph.as_default():
        if(structure == None):
            structure = DEFAULT_STRUCTURE

        model = Sequential()
        for i, layer in enumerate(structure):
            if(layer[0] == "dense"): # Dense class
                if(i == 0): # Input layer
                    model.add(Dense(layer[1]["units"], activation=layer[1]["activation"], input_dim=input_size))
                else: # Hidden layers
                    model.add(Dense(layer[1]["units"], activation=layer[1]["activation"]))
        model.add(Dense(output_size, activation="linear")) # Output layer

        # Optimizer
        adam = Adam(lr=learningRate)

        # Compile model
        model.compile(loss='mean_squared_error', optimizer=adam)
        model.summary()

    return model