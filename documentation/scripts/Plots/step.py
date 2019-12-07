import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
t = np.arange(-5.0, 5.0, 0.01)
s = []

for val in t:
    s.append(0 if(val < 0) else 1)

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='x', ylabel='B(x)')
ax.grid()

plt.show()