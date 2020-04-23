import numpy as np
import matplotlib.pyplot as plt

data01_num, data01_time, data01_prog = np.loadtxt("1core-1process.txt", unpack=True)
#print(data01_num)

plt.plot(data01_time, data01_num)
plt.savefig("test.png")
#plt.show()
