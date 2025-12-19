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

print("Imported. Ready.")


# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------
def run_wake_model(lease_area, altitude):
    """
    Run wake model for a chosen lease area and altitude.

    Parameters
    ----------
    lease_area : str
        Name of the lease area folder inside 'sites/'.
    altitude : str or int
        Altitude identifier used in histo_<altitude>.csv
    """

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
    TI_val = 0.00
    TI_array = np.full((len(wd), len(ws)), TI_val)

    site = XRSite(
        ds=xr.Dataset(
            data_vars={
                'P':  (('wd', 'ws'), P_wd_ws),
                'TI': (('wd', 'ws'), TI_array),   # <-- add TI
                },
            coords={'wd': wd, 'ws': ws}
            )
        )

    # Set up model + cost
    wind_turbines = IEA37_WindTurbines()
    wfmodel = IEA37SimpleBastankhahGaussian(site, wind_turbines)

    # Two dummy turbine positions
    x = [-0.5, -1.5, 100]
    y = [-0.5, -1.5, 100]

    costmodel = PyWakeAEPCostModelComponent(
        wfmodel,
        n_wt=3,
        wd=wd,
        ws=ws
    )

    # ---------------------------------------------------------
    # Helper function inside main function
    # ---------------------------------------------------------
    def plot_boundary(name):
        tf = TopFarmProblem(
            design_vars={'x': x, 'y': y},
            cost_comp=costmodel,
            constraints=[XYBoundaryConstraint(boundary, 'polygon'),
                         SpacingConstraint(1200)],
            plot_comp=XYPlotComp()
        )

        tf.evaluate()

        plt.figure(figsize=(8, 8))
        plt.title(name)
        tf.plot_comp.plot_constraints()
        plt.plot(boundary[:, 0], boundary[:, 1], '.r', label='Boundary points')
        plt.axis('equal')
        plt.show()

    # Run the boundary plot
    plot_boundary(f"Boundary for {lease_area} @ {altitude}m")



# ---------------------------------------------------------
# CALL EXAMPLES (uncomment to run in Spyder)
# ---------------------------------------------------------

run_wake_model("0499", '160')
# run_wake_model("OCS_EA", 140)
# run_wake_model("some_area_name", "80")