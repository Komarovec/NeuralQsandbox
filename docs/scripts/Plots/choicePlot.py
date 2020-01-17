import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from keras.models import load_model

try:
    model = load_model("model_big.h5")
except:
    print("Cannot load model!")
    model = None

steps = 50

def generateStates():
    states = []
    for i in range(0, 100, int(100/steps)):
        for j in range(0, 100, int(100/steps)):
            state = []
            state.append(0.8)
            state.append(i/100)
            state.append(j/100)
            states.append(np.array([state]))
        
    return np.array(states)

def calculateActions(states, actionSpace):
    actions = []
    for i in range(0, steps):
        actionsInRow = []
        for j in range(0, steps):
            actionsInRow.append(model.predict_on_batch(states[j+(i*steps)])[0][actionSpace])
        
        actions.append(actionsInRow)
    
    return np.array(actions)

def main():
    # Generate state data
    states = generateStates()
    forward_prop = calculateActions(states, 0)
    left_prop = calculateActions(states, 1)
    right_prop = calculateActions(states, 2)

    sum_of_matrix = forward_prop + left_prop + right_prop

    left_prop_g = left_prop/sum_of_matrix
    right_prop_g = right_prop/sum_of_matrix
    forward_prop_g = forward_prop/sum_of_matrix

    X = np.arange(0, 1, 1/steps)
    Y = np.arange(0, 1, 1/steps)
    X, Y = np.meshgrid(X, Y)

    fig = plt.figure()
    ax = Axes3D(fig)

    #ax.plot_surface(X, Y, forward_prop_g, rstride=1, cstride=1, cmap=cm.cividis)
    ax.plot_surface(X, Y, left_prop_g, rstride=1, cstride=1, cmap=cm.viridis)
    ax.plot_surface(X, Y, right_prop_g, rstride=1, cstride=1, cmap=cm.inferno)

    plt.xlabel('Right sensor')
    plt.ylabel('Left sensor')

    plt.show()

if __name__ == "__main__":
    if(model != None):
        main()