#AI Framework
from keras.models import Sequential
import keras

#Creates sequential model
def SequentialModel(input_size, output_size, learningRate, structure=None):
    #Default model
    if(structure==None):
        #Create model
        model = keras.Sequential([
            keras.layers.Dense(64, activation="relu", input_dim=input_size),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(output_size, activation="linear")
        ])
    else:
        pass
        #Custom model editing

    #Optimizer
    adam = keras.optimizers.Adam(lr=learningRate)

    #Compile model
    model.compile(loss='mean_squared_error', optimizer=adam)

    return model