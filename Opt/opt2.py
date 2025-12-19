import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

print("Importing libraries. This may take a while... ")
from py_wake.site import XRSite
import xarray as xr
from topfarm import TopFarmProblem
from topfarm.plotting import XYPlotComp
from topfarm.constraint_components.boundary import XYBoundaryConstraint
from topfarm.constraint_components.spacing import SpacingConstraint
from topfarm.cost_models.py_wake_wrapper import PyWakeAEPCostModelComponent
from py_wake.deficit_models.gaussian import IEA37SimpleBastankhahGaussian
from py_wake.examples.data.iea37 import IEA37_WindTurbines
from topfarm.easy_drivers import EasyScipyOptimizeDriver   # <-- NEW
from matplotlib.path import Path

print("Imported. Ready.")


def run_wake_model(lease_area, altitude, n_wt=30):
    """
    Run wake model for a chosen lease area and altitude.

    Parameters
    ----------
    lease_area : str
        Name of the lease area folder inside 'sites/'.
    altitude : str or int
        Altitude identifier used in histo_<altitude>.csv
    n_wt : int
        Number of turbines to place.
    """

    # Ensure output folder exists
    os.makedirs("output", exist_ok=True)

    # Load data
    boundary = np.load(f"sites/{lease_area}/boundary.npy")
    histo = pd.read_csv(f"sites/{lease_area}/histo_{altitude}.csv")

    # Extract wind direction + speed bins
    wd = histo["dirbins"].unique().tolist()
    ws = histo["speedbins"].unique().tolist()

    # Build probability matrix
    P_wd_ws = [[0] * len(ws) for _ in range(len(wd))]
    for r in histo.itertuples():
        di = wd.index(r.dirbins)
        si = ws.index(r.speedbins)
        P_wd_ws[di][si] = r.count

    # Build PyWake site object
    TI_val = 0.08  # non-zero turbulence intensity is more realistic
    TI_array = np.full((len(wd), len(ws)), TI_val)

    site = XRSite(
        ds=xr.Dataset(
            data_vars={
                'P':  (('wd', 'ws'), P_wd_ws),
                'TI': (('wd', 'ws'), TI_array),
            },
            coords={'wd': wd, 'ws': ws}
        )
    )

    # Set up model + cost
    wind_turbines = IEA37_WindTurbines()
    wfmodel = IEA37SimpleBastankhahGaussian(site, wind_turbines)

    # Initial turbine positions (dummy layout – optimizer will move them)
    # Here, just place them in a small cluster near origin
    #x0 = np.linspace(-1_000, 1_000, n_wt)
    #y0 = np.zeros(n_wt)-10000


    def random_points_in_polygon(boundary, n_points):
        """
        Sample n_points uniformly in the bounding box and keep those inside
        the polygon defined by `boundary` (array of shape (N,2)).
        """
        poly_path = Path(boundary)

        x_min, y_min = boundary.min(axis=0)
        x_max, y_max = boundary.max(axis=0)

        xs = []
        ys = []

        # Simple rejection sampling
        while len(xs) < n_points:
            # sample a batch to keep it fast
            batch_size = max(10 * n_points, 100)
            cand_x = np.random.uniform(x_min, x_max, batch_size)
            cand_y = np.random.uniform(y_min, y_max, batch_size)
            cand_pts = np.vstack((cand_x, cand_y)).T

            inside = poly_path.contains_points(cand_pts)
            for (cx, cy), ok in zip(cand_pts, inside):
                if ok:
                    xs.append(cx)
                    ys.append(cy)
                    if len(xs) == n_points:
                        break

        return np.array(xs), np.array(ys)

    # Use random initial layout
    x0, y0 = random_points_in_polygon(boundary, n_wt)
    
    costmodel = PyWakeAEPCostModelComponent(
        wfmodel,
        n_wt=n_wt,
        wd=wd,
        ws=ws
    )

    # --------------- Optimize & Plot ---------------
    driver = EasyScipyOptimizeDriver()   # <-- optimization driver

    tf = TopFarmProblem(
        design_vars={'x': x0, 'y': y0},
        cost_comp=costmodel,
        constraints=[
            XYBoundaryConstraint(boundary, 'polygon'),
            SpacingConstraint(1200)
        ],
        plot_comp=XYPlotComp(),
        driver=driver
    )

    # This actually runs the optimization
    cost, state, recorder = tf.optimize()

    x_opt = state['x']
    y_opt = state['y']

    print("Optimal cost (negative AEP or similar):", cost)
    print("Optimal x:", x_opt)
    print("Optimal y:", y_opt)

    # Save optimized turbine positions
    outpath = f"output/opt_layout_{lease_area}_{altitude}m.npy"
    np.save(outpath, {"x": x_opt, "y": y_opt})
    print(f"Saved optimized layout to {outpath}")

    # Plot boundary + optimized layout
    plt.figure(figsize=(8, 8))
    plt.title(f"Optimized layout for {lease_area} @ {altitude}m")
    tf.plot_comp.plot_constraints()
    plt.plot(boundary[:, 0], boundary[:, 1], '.r', label='Boundary points')
    plt.scatter(x_opt, y_opt, c='k', marker='x', s=50, label='Turbines')
    plt.legend()
    plt.axis('equal')

    fig_outpath = f"output/opt_layout_{lease_area}_{altitude}m.png"
    plt.savefig(fig_outpath, dpi=300, bbox_inches='tight')
    print(f"Saved figure to {fig_outpath}")

    plt.show()

    # Optionally return results if you want to use them elsewhere
    return x_opt, y_opt, cost

run_wake_model("0499", '140')
# Example Spyder call
# run_wake_model("0499", "160", n_wt=2)