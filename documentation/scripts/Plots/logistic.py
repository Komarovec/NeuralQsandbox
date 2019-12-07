import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
t = np.arange(-5.0, 5.0, 0.01)
exp_t = np.exp(t)
s = exp_t / (exp_t + 1)

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='x', ylabel='S(x)')
ax.grid()

plt.show()