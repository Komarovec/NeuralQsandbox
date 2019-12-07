import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
t = np.arange(-5.0, 5.0, 0.01)

s = (t + abs(t)) / 2

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='x', ylabel='R(x)')
ax.grid()

plt.show()