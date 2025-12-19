import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


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
            f"Column '{ws_col}' not found in whole.csv. "
        )

    df = df[[ws_col]].rename(columns={ws_col: 'ws'})
    return df


def build_representative_year_daily(df):
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
    year = 2019
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

    # Build design matrix
    X = np.column_stack([
        np.ones_like(t),
        np.cos(2 * np.pi * t / 365),
        np.sin(2 * np.pi * t / 365)
    ])

    # Least squares fit
    coeffs, *_ = np.linalg.lstsq(X, y, rcond=None)
    a0, a1, b1 = coeffs

    # Build fitted curve
    fit_vals = a0 + a1*np.cos(2*np.pi*t/365) + b1*np.sin(2*np.pi*t/365)

    fit_df = rep_year.copy()
    fit_df['ws_fit'] = fit_vals

    params = {
        'a0': a0,
        'a1': a1,
        'b1': b1
    }

    return fit_df, params


def plot_rep_with_fit(fit_df, lease_area, height_m=100, params=None):
    """
    Plot representative year and trig-fit curve together.
    """
    plt.figure(figsize=(11, 5))
    plt.plot(fit_df['date'], fit_df['ws_rep'], label='Daily Mean (Representative Year)', alpha=0.6)
    plt.plot(fit_df['date'], fit_df['ws_fit'], label='Trig Fit', linewidth=2)

    plt.xlabel("Date")
    plt.ylabel(f"Daily mean wind speed at {height_m}m [m/s]")
    plt.title(f"Representative Year \nLease area {lease_area}")
    plt.grid(alpha=0.3)
    plt.legend()

    if params is not None:
        txt = f"a0 = {params['a0']:.3f}\na1 = {params['a1']:.3f}\nb1 = {params['b1']:.3f}"
        plt.annotate(txt, xy=(0.02, 0.7), xycoords='axes fraction',
                     fontsize=10, bbox=dict(boxstyle="round", fc="w", alpha=0.8))

    plt.tight_layout()
    plt.show()


# ---------------------------------------
# Example usage
# ---------------------------------------
if __name__ == "__main__":
    lease_area = "0499"
    height_m = 100

    df_ws = load_whole_with_datetime(lease_area, height_m=height_m)
    rep = build_representative_year_daily(df_ws)

    fit_df, params = fit_trigonometric_model(rep)
    print("Fitted parameters:", params)

    plot_rep_with_fit(fit_df, lease_area, height_m=height_m, params=params)