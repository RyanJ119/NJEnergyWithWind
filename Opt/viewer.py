from helpers import outliner
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np

if len(sys.argv) < 2:
    PNG = "0541"
else:
    PNG = str(sys.argv[1])

if len(sys.argv) < 3:
    OUTLINE = None
else:
    OUTLINE = sys.argv[2]
    g = np.load(OUTLINE, allow_pickle=True).item()

cplr = outliner.outline(f"sites/define/{PNG}.png")

x_min, y_min = np.min(cplr, axis=0)
x_max, y_max = np.max(cplr, axis=0)

fig, ax = plt.subplots()
polygon = Polygon(cplr, closed=True, facecolor='lightblue', edgecolor='blue')
ax.add_patch(polygon)
ax.set_xlim(x_min - 1000, x_max + 1000)
ax.set_ylim(y_min - 1000, y_max + 1000)
plt.gca().set_aspect('equal')

if OUTLINE:
    plt.scatter(g['x'], g['y'])

plt.show()