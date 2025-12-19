import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np


def plot_wind_rose(lease_area, altitude):
    """
    Plot a wind rose for a given lease area and altitude.

    Parameters
    ----------
    lease_area : str
        Name of the lease area folder inside './sites/'.
    altitude : str or int
        Altitude identifier used in histo_<altitude>.csv
    """

    # Load histogram data
    his = pd.read_csv(f"./sites/{lease_area}/histo_{altitude}.csv", index_col=0)

    # Optional: max count (currently not used but kept for reference)
    plotmax = (
        his.drop(columns="speedbins")
        .groupby("dirbins")["count"]
        .sum()
        .max()
    )

    dirsorted = his.sort_values(["dirbins", "speedbins"])
    print(dirsorted)

    numdirs = his["dirbins"].nunique()
    numspeeds = his["speedbins"].nunique()

    # Colormap for speed bins
    cmap = mpl.colormaps["viridis_r"]
    colors = cmap(np.linspace(0, 1, numspeeds))

    # Polar plot
    ax = plt.subplot(111, polar=True)
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

        # New direction bin
        if currdir != d:
            i = 0
            currbot = 0
            ticks.append(td)
            ticklabels.append(str(d) + "°")
            if first is None:
                first = True
            elif first is True:
                first = False

        currdir = d

        b = ax.bar(
            x=td,
            height=f,
            width=(2 * np.pi) / numdirs,
            bottom=currbot,
            color=colors[i],
        )

        if first:
            legenditems[0].append(b)
            legenditems[1].append(s)

        currbot += f
        i += 1

    ax.set_anchor("W")
    ax.set_xticks(ticks)
    ax.set_yticklabels([])
    ax.set_xticklabels(ticklabels)
    ax.xaxis.set_tick_params(width=1, grid_alpha=0.5)
    ax.spines["polar"].set_visible(False)
    ax.yaxis.set_tick_params(width=1, grid_alpha=0.5)

    ax.set_title(
        f"Wind rose for lease area {lease_area} at altitude {altitude}m",
        y=1.08,
        fontweight="bold",
    )

    ax.legend(
        handles=legenditems[0],
        labels=legenditems[1],
        loc="upper right",
        title="Bin Avg. m/s",
        bbox_to_anchor=(1.45, 1.0),
    )

    plt.show()


# ---------------------------------------------------------
# Example calls for Spyder (uncomment and edit as needed)
# ---------------------------------------------------------
plot_wind_rose("0499", '100')
# plot_wind_rose("lease1", 150)