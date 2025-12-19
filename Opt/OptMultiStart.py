#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 24 14:33:49 2025

@author: ryanweightman
"""

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
from topfarm.easy_drivers import EasyScipyOptimizeDriver
from matplotlib.path import Path  # for point-in-polygon

print("Imported. Ready.")


def random_points_in_polygon(boundary, n_points, rng=None):
    """
    Sample n_points uniformly in the bounding box and keep those inside
    the polygon defined by `boundary` (array of shape (N,2)).
    """
    if rng is None:
        rng = np.random.default_rng()

    poly_path = Path(boundary)

    x_min, y_min = boundary.min(axis=0)
    x_max, y_max = boundary.max(axis=0)

    xs = []
    ys = []

    # Simple rejection sampling
    while len(xs) < n_points:
        batch_size = max(10 * n_points, 100)
        cand_x = rng.uniform(x_min, x_max, batch_size)
        cand_y = rng.uniform(y_min, y_max, batch_size)
        cand_pts = np.vstack((cand_x, cand_y)).T

        inside = poly_path.contains_points(cand_pts)
        for (cx, cy), ok in zip(cand_pts, inside):
            if ok:
                xs.append(cx)
                ys.append(cy)
                if len(xs) == n_points:
                    break

    return np.array(xs), np.array(ys)


def run_wake_model_multistart(lease_area, altitude, n_wt=2, n_starts=5, seed=None):
    """
    Run wake model for a chosen lease area and altitude using multiple random
    initial layouts, and keep the best (max AEP).

    Parameters
    ----------
    lease_area : str
        Name of the lease area folder inside 'sites/'.
    altitude : str or int
        Altitude identifier used in histo_<altitude>.csv
    n_wt : int
        Number of turbines.
    n_starts : int
        Number of random initial layouts to try.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    best_x, best_y : np.ndarray
        Optimized turbine coordinates for the best run.
    best_AEP : float
        Best AEP found (GWh or model units).
    """

    os.makedirs("output", exist_ok=True)
    rng = np.random.default_rng(seed)

    # ---------- Load site / wind data once ----------
    boundary = np.load(f"sites/{lease_area}/boundary.npy")
    histo = pd.read_csv(f"sites/{lease_area}/histo_{altitude}.csv")

    wd = histo["dirbins"].unique().tolist()
    ws = histo["speedbins"].unique().tolist()

    # Probability matrix
    P_wd_ws = [[0] * len(ws) for _ in range(len(wd))]
    for r in histo.itertuples():
        di = wd.index(r.dirbins)
        si = ws.index(r.speedbins)
        P_wd_ws[di][si] = r.count

    # Turbulence intensity
    TI_val = 0.08
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

    wind_turbines = IEA37_WindTurbines()
    wfmodel = IEA37SimpleBastankhahGaussian(site, wind_turbines)

    costmodel = PyWakeAEPCostModelComponent(
        wfmodel,
        n_wt=n_wt,
        wd=wd,
        ws=ws
    )

    best_cost = None     # remember: cost = -AEP
    best_state = None

    # ---------- Multi-start loop ----------
    for k in range(n_starts):
        print(f"\n=== Start {k+1}/{n_starts} ===")

        x0, y0 = random_points_in_polygon(boundary, n_wt, rng=rng)

        driver = EasyScipyOptimizeDriver()

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

        cost, state, recorder = tf.optimize()
        AEP = -cost  # since cost = -AEP

        print(f"  cost = {cost:.4e},  AEP = {AEP:.4e}")

        if (best_cost is None) or (cost < best_cost):
            best_cost = cost
            best_state = state.copy()
            best_tf = tf  # keep last TopFarmProblem for plotting

    # ---------- Use best result ----------
    best_x = np.array(best_state['x'])
    best_y = np.array(best_state['y'])
    best_AEP = -best_cost

    print("\n=== Best layout over all starts ===")
    print("Best cost (=-AEP):", best_cost)
    print("Best AEP:", best_AEP)
    print("Best x:", best_x)
    print("Best y:", best_y)

    # Save layout
    layout_path = f"output/opt_layout_{lease_area}_{altitude}m_multistart.npy"
    np.save(layout_path, {"x": best_x, "y": best_y, "AEP": best_AEP})
    print(f"Saved best layout to {layout_path}")

    # Plot best layout
    plt.figure(figsize=(8, 8))
    plt.title(f"Best optimized layout for {lease_area} @ {altitude}m\n({n_starts} starts)")
    best_tf.plot_comp.plot_constraints()
    plt.plot(boundary[:, 0], boundary[:, 1], '.r', label='Boundary points')
    plt.scatter(best_x, best_y, c='k', marker='x', s=50, label='Turbines')
    plt.legend()
    plt.axis('equal')

    fig_path = f"output/opt_layout_{lease_area}_{altitude}m_multistart.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"Saved figure to {fig_path}")

    plt.show()

    return best_x, best_y, best_AEP

best_x, best_y, best_AEP = run_wake_model_multistart("0499", "160", n_wt=100, n_starts=10, seed=42)
