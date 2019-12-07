
import random
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras

# Konstanty
a = 1
b = 0
power = 1

#G enerace dat
def generateData(val):
    data = np.empty((0,2), int)
    for i in range(0, val):
        posX = random.random()
        posY = random.random()
        data = np.append(data, [[posX,posY]], axis=0)
    return data

# Testovani dat
def testData(data):
    label = np.empty((0,1), int)
    for i in data:
        if(i[1] < a*pow(i[0],power)+b):
            label = np.append(label, 0)
        else:
            label = np.append(label, 1)
    return label

# Plotting
def plotData(data, label): 
    i = 0
    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.set_ylabel('y')
    ax1.set_xlabel('x')
    for item in data:
        ax1.plot(item[0], item[1], 'o', color = (label[i],1-label[i],0.0))
        i = i + 1
    plt.show()


def main(*args):
    train_data = generateData(5000)
    train_label = testData(train_data)

    test_data = generateData(1000)
    test_label = testData(test_data)

    print("Data shape:")
    print("Data shape: "+str(train_data.shape))
    print("Data: "+str(train_data))
    print("Index: "+str(train_data[0,0]))
    print("----------------")

    plotData(test_data, test_label)

    #Single layer perceptron
    model = keras.Sequential([ 
        keras.layers.Dense(16, input_shape=(2,)),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(1, activation=tf.nn.sigmoid)
    ])

    model.compile(optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy'])

    history = model.fit(train_data, 
                        train_label,
                        batch_size=128, 
                        epochs=50)

    test_loss, test_acc = model.evaluate(test_data, test_label)
    print('Test accuracy:', test_acc)

    predictions = model.predict(test_data)
    print("Prediction: "+str(predictions[0].shape))

    predictionsTest = []
    for i in predictions:
        predictionsTest.append(i[0])

    plotData(test_data, predictionsTest)

if __name__ == "__main__":
    main()