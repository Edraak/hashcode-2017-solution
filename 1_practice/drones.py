import matplotlib.pyplot as plt
import numpy as np

R, C, L, H = 0, 0, 0, 0

with open("small.in", "r") as ins:
    R, C, L, H = map(int, ins.readline().split())
    array = []
    for line in ins.read().splitlines():
        array.append(map(ord, line))

print array

g = array

plt.subplot(211)
plt.imshow(g)
plt.savefig('blkwht.png')

plt.show()
