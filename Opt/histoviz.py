#!.venv/bin/python
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
import sys

if len(sys.argv) < 3:
    print("Usage: ./histoviz.py [BOUNDARYNAME] [HEIGHTNAME]")
    exit(1)
LEASE_AREA = sys.argv[1]
ALTITUDE = sys.argv[2]
his = pd.read_csv(f"./sites/{LEASE_AREA}/histo_{ALTITUDE}.csv", index_col=0)
plotmax = his.drop(columns="speedbins").groupby("dirbins")['count'].sum().max()
dirsorted = his.sort_values(["dirbins", "speedbins"])
print(dirsorted)

numdirs = his["dirbins"].nunique()
numspeeds = his["speedbins"].nunique()

cmap = mpl.colormaps['viridis_r']
colors = cmap(np.linspace(0, 1, numspeeds))

ax = plt.subplot(111, polar=True);
first = None
currdir = None
currbot = 0
ticks = []
ticklabels = []
legenditems = ([], [])
for _, r in dirsorted.iterrows():
    d = r["dirbins"]
    td = ((np.pi / 2) - np.deg2rad(d)) % (np.pi * 2)
    s = r["speedbins"]
    f = r["count"]
    if currdir != d:
        i = 0
        currbot = 0
        ticks.append(td)
        ticklabels.append(str(d) + "°")
        if first == None:
            first = True
        elif first == True:
            first = False
    currdir = d
    b = ax.bar(x = td, height=f, width=(2 * np.pi) / numdirs, bottom=currbot, color=colors[i]);
    if first:
        legenditems[0].append(b)
        legenditems[1].append(s)
    currbot += f
    i+=1

ax.set_anchor("W")
ax.set_xticks(ticks)
ax.set_yticklabels([])
ax.set_xticklabels(ticklabels)
ax.xaxis.set_tick_params(width=1, grid_alpha=0.5)
ax.spines['polar'].set_visible(False)
ax.yaxis.set_tick_params(width=1, grid_alpha=0.5)
ax.set_title(f"Wind rose for lease area {LEASE_AREA} at altitude {ALTITUDE}m", y=1.08, fontweight='bold')
ax.legend(handles=legenditems[0], labels=legenditems[1], loc="upper right", title="Bin Avg. m/s", bbox_to_anchor=(1.45, 1.0))
plt.show()