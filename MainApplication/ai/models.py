# AI Framework
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

# Creates sequential model
def SequentialModel(input_size, output_size, learningRate, structure=None):
    print("creating new model")
    
    # Example structure
    #structure = [[Dense, {"units":32, "activation":"relu"}],
    #             [Dense, {"units":64, "activation":"relu"}],
    #             [Dense, {"units":32, "activation":"relu"}]]

    # Default model
    if(structure==None):
        # Create model
        model = Sequential([
            Dense(64, activation="relu", input_dim=input_size),
            Dense(128, activation="relu"),
            Dense(64, activation="relu"),
            Dense(output_size, activation="linear")
        ])
    # Custom model
    else:
        model = Sequential()
        for i, layer in enumerate(structure):
            if(layer[0] == Dense): # Dense class
                if(i == 0): # Input layer
                    model.add(layer[0](layer[1]["units"], activation=layer[1]["activation"], input_dim=input_size))
                else: # Hidden layers
                    model.add(layer[0](layer[1]["units"], activation=layer[1]["activation"]))
        model.add(Dense(output_size, activation="linear")) # Output layer

    # Optimizer
    adam = Adam(lr=learningRate)

    # Compile model
    model.compile(loss='mean_squared_error', optimizer=adam)

    return model