from helpers import outliner
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np


def plot_boundary_png(png_code="0541", outline_path=None):
    """
    Plot lease boundary from a PNG outline, with optional scatter overlay.

    Parameters
    ----------
    png_code : str
        The 4-digit code of the PNG in sites/define/ (e.g. "0541").
    outline_path : str or None
        Optional path to a .npy file containing a dict with 'x' and 'y' keys
        to scatter on top of the polygon.
    """
    # Get polygon from PNG via your helper
    cplr = outliner.outline(f"sites/define/{png_code}.png")

    x_min, y_min = np.min(cplr, axis=0)
    x_max, y_max = np.max(cplr, axis=0)

    fig, ax = plt.subplots()
    polygon = Polygon(cplr, closed=True, facecolor='lightblue', edgecolor='blue')
    ax.add_patch(polygon)
    ax.set_xlim(x_min - 1000, x_max + 1000)
    ax.set_ylim(y_min - 1000, y_max + 1000)
    ax.set_aspect('equal', adjustable='box')

    # Optional overlay from .npy file
    if outline_path is not None:
        g = np.load(outline_path, allow_pickle=True).item()
        plt.scatter(g['x'], g['y'])

    plt.title(f"Lease outline {png_code}")
    plt.show()


# ---------------------------------------------------------
# Example calls for Spyder (uncomment to use)
# ---------------------------------------------------------
# plot_boundary_png("0541")
plot_boundary_png("0499", )