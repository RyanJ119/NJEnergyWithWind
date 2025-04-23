#!.venv/bin/python

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import sys

print("Importing libraries. This may take a while... ")
from py_wake.site import XRSite
import xarray as xr
from topfarm import TopFarmProblem
from topfarm.plotting import XYPlotComp
from topfarm.constraint_components.boundary import XYBoundaryConstraint, CircleBoundaryConstraint
from topfarm.constraint_components.spacing import SpacingConstraint
from topfarm.cost_models.cost_model_wrappers import CostModelComponent
from topfarm.cost_models.py_wake_wrapper import PyWakeAEPCostModelComponent
from py_wake.deficit_models.gaussian import IEA37SimpleBastankhahGaussian
from py_wake.examples.data.iea37 import IEA37_WindTurbines, IEA37Site
from topfarm.easy_drivers import EasyScipyOptimizeDriver
from topfarm.examples.iea37 import get_iea37_initial, get_iea37_constraints, get_iea37_cost

print("Imported. Starting process.")

LEASE_AREA = sys.argv[1]
ALTITUDE = sys.argv[2]

boundary = np.load(f"sites/{LEASE_AREA}/boundary.npy")
histo = pd.read_csv(f"sites/{LEASE_AREA}/histo_{ALTITUDE}.csv")

wd = histo["dirbins"].unique().tolist()
ws = histo["speedbins"].unique().tolist()

P_wd_ws = [ [0] * len(ws) for i in range(len(wd)) ]
for r in histo.itertuples():
    cd, cs = r.dirbins, r.speedbins
    di, si = wd.index(cd), ws.index(cs)
    P_wd_ws[di][si] = r.count

site = XRSite(
    ds=xr.Dataset(
        data_vars={
                   'P': (('wd', 'ws'), P_wd_ws),
                   },
        coords={'ws': ws, 'wd': wd}))

# site = IEA37Site(9)

# n_wt = 9
n_wd = len(wd)

x = [-0.5,-1.5]
y = [-.5,-1.5]

wind_turbines = IEA37_WindTurbines()
wfmodel = IEA37SimpleBastankhahGaussian(site, wind_turbines) 
costmodel = PyWakeAEPCostModelComponent(wfmodel, 2, wd=wd, ws=ws)
# costmodel = CostModelComponent(input_keys=[], n_wt=2, cost_function=lambda : 1)
# driver = EasyScipyOptimizeDriver()

def plot_boundary(name):
    tf = TopFarmProblem(
        design_vars={'x':x, 'y': y}, # setting up the turbine positions as design variables
        cost_comp=costmodel, # using dummy cost model
        constraints=[XYBoundaryConstraint(boundary, 'polygon'), SpacingConstraint(1200)], # constraint set up for the boundary type provided
        plot_comp=XYPlotComp()) # support plotting function
    tf.evaluate()

    plt.figure()
    plt.title(name)
    tf.plot_comp.plot_constraints() # plot constraints is a helper function in topfarm to plot constraints
    plt.plot(boundary[:,0], boundary[:,1],'.r', label='Boundary points') # plot the boundary points
    plt.axis('equal')
    plt.show()

plot_boundary('convex_hull')