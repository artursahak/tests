import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np

coords=pd.read_csv('coords.csv')

plt.legend(['Custom Brush soft'])
plt.xlabel('frames')
plt.ylabel('width')

coordX = []
coordY = []
coordW = []
coordX.append(coords.x)
coordY.append(coords.y)
coordW.append(coords.width)

#plt.grid()
r = random.random()
b = random.random()
g = random.random()
color = (r, g, b)

plot2 = plt.figure(1)
for width ,x , y in zip(coordW ,coordX, coordY):
    rgb = np.random.rand(3,)
    plt.scatter(x, y, c=[rgb],linewidth=width)
#plt.plot(coords.x,coords.y,'o',c=color,linewidth=10)

plt.show()

