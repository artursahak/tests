import matplotlib.pyplot as plt
import csv
import pandas as pd
import numpy as np
from matplotlib.animation import FuncAnimation

coords=pd.read_csv('coords.csv')

print(type(coords))
print(coords.width)


plt.legend(['Custom Brush soft'])
plt.xlabel('frames')
plt.ylabel('width')

plot1 = plt.figure(1)

plt.grid()
plt.fill(coords.width,color='orange')
plt.plot(coords.width)

plot2 = plt.figure(2)

plt.plot(coords.x,coords.y,linewidth=4)

plt.show()




