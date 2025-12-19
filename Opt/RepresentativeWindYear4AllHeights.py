import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------
# Configuration
# ------------------------

LEASE_AREAS = ["0499", "0532", "0537", "0538", "0539",
               "0541", "0542", "0544", "0549", "0570"]

# Heights list (unique heights, ignoring duplicated 80)
HEIGHTS = [10, 20, 40, 60, 80, 100, 120, 140,180,  160, 200]


# ------------------------
# Core functions
# ------------------------

def load_whole_with_datetime(lease_area, height_m=100):
    """
    Load sites/<lease_area>/whole.csv and return a DataFrame with a DatetimeIndex
    and a single wind-speed column at the desired height.
    """
    path = Path(f"./sites/{lease_area}/whole.csv")
    df = pd.read_csv(path)

    # Build datetime from separate columns
    dt = pd.to_datetime(
        df[['Year', 'Month', 'Day', 'Hour', 'Minute']]
        .rename(columns={
            'Year': 'year',
            'Month': 'month',
            'Day': 'day',
            'Hour': 'hour',
            'Minute': 'minute'
        })
    )
    df['time'] = dt
    df = df.set_index('time').sort_index()

    # Choose the wind-speed column for the requested height
    ws_col = f"Wind Speed at {height_m}m (m/s)"
    if ws_col not in df.columns:
        raise ValueError(
            f"Column '{ws_col}' not found in whole.csv for lease {lease_area}."
        )

    df = df[[ws_col]].rename(columns={ws_col: 'ws'})
    return df


def build_representative_year_daily(df, year=2025):
    """
    Build a representative (synthetic) year of daily mean wind speeds.
    """
    # Daily means
    daily = df['ws'].resample('D').mean().dropna()

    doy = daily.index.dayofyear
    daily_by_doy = daily.groupby(doy).mean()

    # Drop leap day if present
    if 366 in daily_by_doy.index:
        daily_by_doy = daily_by_doy.loc[daily_by_doy.index <= 365]

    # Construct synthetic year
    dates = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='D')

    ws_rep = [daily_by_doy[d] for d in range(1, 366)]

    rep_year = pd.DataFrame({
        'date': dates,
        'dayofyear': np.arange(1, 366),
        'ws_rep': ws_rep
    })
    return rep_year


def fit_trigonometric_model(rep_year):
    """
    Fit a simple trig model:
        ws(t) = a0 + a1*cos(2πt/365) + b1*sin(2πt/365)

    Returns
    -------
    fit_df : DataFrame with fitted values
    params : dict of fitted parameters
    """

    t = rep_year['dayofyear'].values
    y = rep_year['ws_rep'].values

    # Build design matrix: [1, cos(2π t / 365), sin(2π t / 365)]
    X = np.column_stack([
        np.ones_like(t),
        np.cos(2 * np.pi * t / 365),
        np.sin(2 * np.pi * t / 365)
    ])

    # Least squares fit
    coeffs, *_ = np.linalg.lstsq(X, y, rcond=None)
    a0, a1, b1 = coeffs

    # Build fitted curve
    fit_vals = a0 + a1 * np.cos(2 * np.pi * t / 365) + b1 * np.sin(2 * np.pi * t / 365)

    fit_df = rep_year.copy()
    fit_df['ws_fit'] = fit_vals

    params = {
        'a0': a0,
        'a1': a1,
        'b1': b1
    }

    return fit_df, params


# ------------------------
# Batch run & CSV export
# ------------------------

def run_all_sites_and_heights_3term(output_csv="trig3_params_all_sites_heights.csv"):
    """
    For all lease areas and heights, fit the 3-term trig model and save parameters to CSV.

    Returns
    -------
    params_df : pandas.DataFrame
        Columns: ['lease_area', 'height_m', 'a0', 'a1', 'b1']
    """
    rows = []

    for lease in LEASE_AREAS:
        for h in HEIGHTS:
            try:
                print(f"Processing lease {lease}, height {h}m...")
                df_ws = load_whole_with_datetime(lease, height_m=h)
                rep = build_representative_year_daily(df_ws, year=2025)
                _, params = fit_trigonometric_model(rep)
                rows.append({
                    "lease_area": lease,
                    "height_m": h,
                    "a0": params["a0"],
                    "a1": params["a1"],
                    "b1": params["b1"],
                })
            except Exception as e:
                print(f"  Skipping lease {lease}, height {h}m due to error: {e}")

    params_df = pd.DataFrame(rows)
    params_df.to_csv(output_csv, index=False)
    print(f"\nSaved 3-term trig parameters to {output_csv}")
    return params_df


# ------------------------
# Plotting all trig functions
# ------------------------

def plot_all_trig_functions_3term(params_df, year=2025):
    """
    Plot the 3-term trig-fit curves for all lease-area / height combinations.

    Parameters
    ----------
    params_df : pandas.DataFrame
        Output from run_all_sites_and_heights_3term (or loaded from CSV).
    year : int
        Synthetic year used for plotting the time axis.
    """
    t = np.arange(1, 366)
    dates = pd.date_range(start=f"{year}-01-01", periods=365, freq="D")

    plt.figure(figsize=(12, 7))

    for _, row in params_df.iterrows():
        a0 = row["a0"]
        a1 = row["a1"]
        b1 = row["b1"]
        lease = row["lease_area"]
        h = int(row["height_m"])

        ws_fit = a0 + a1 * np.cos(2 * np.pi * t / 365) + b1 * np.sin(2 * np.pi * t / 365)

        label = f"{lease}-{h}m"
        plt.plot(dates, ws_fit, label=label, alpha=0.6)

    plt.xlabel("Date")
    plt.ylabel("Daily mean wind speed [m/s]")
    plt.title("3-term trig-fit representative wind year\nAll lease areas and heights")
    plt.grid(alpha=0.3)
    plt.legend(fontsize=7, ncol=3, bbox_to_anchor=(1.05, 1.0), loc="upper left")
    plt.tight_layout()
    plt.show()


# ---------------------------------------
# Example usage
# ---------------------------------------
if __name__ == "__main__":
    # 1) Run for all sites & heights and save coefficients
    params_df = run_all_sites_and_heights_3term(
        output_csv="trig3_params_all_sites_heights.csv"
    )

    # 2) Plot trig functions for all cases
    plot_all_trig_functions_3term(params_df, year=2025)