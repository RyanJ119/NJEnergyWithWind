import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def bins(whole : pd.DataFrame, height, dirs, speeds):
    SPEED = f"Wind Speed at {height}m (m/s)"
    DIRECTION = f"Wind Direction at {height}m (°)"

    snip = pd.DataFrame({SPEED: whole[SPEED], DIRECTION: whole[DIRECTION]})
    snip[DIRECTION] = snip[DIRECTION].mod(360.0)

    # sns.histplot(snip[SPEED], kde=True, bins=10)
    # plt.show()

    snip['speedbins'] = pd.cut(snip[SPEED], bins=speeds)
    snip['dirbins'] = pd.cut(snip[DIRECTION], bins=np.linspace(0, 360, dirs + 1), labels=[i * (360 / dirs) + (360 / dirs / 2) for i in range(dirs)])
    bin_means = snip.groupby(snip['speedbins'], observed=True)[SPEED].mean().round(3)
    snip['speedbins'] = pd.cut(snip[SPEED], bins=speeds, labels=bin_means)

    return snip.drop(columns=[SPEED, DIRECTION])

def histo(binned_data : pd.DataFrame):
    counts = binned_data.groupby(['speedbins', 'dirbins'], observed=True).size().reset_index(name='count')
    counts['count'] = (counts['count'] / counts['count'].sum())

    return counts.sort_values(["dirbins", "speedbins"]).reset_index(drop=True)

def markov(binned_data : pd.DataFrame, histo : pd.DataFrame): # This is a LEFT stochastic matrix, expressing the COLUMN --> ROW transition.
    matrix = pd.DataFrame()
    for r in histo.itertuples():
        csp = r.speedbins
        cdi = r.dirbins
        neo = pd.DataFrame()
        neo[f"d{cdi}_s{csp}"] = [0] * len(histo)
        matrix = pd.concat([matrix, neo], axis=1)
    first = True
    prevwind = ""
    for r in binned_data.itertuples():
        csp = r.speedbins 
        cdi = r.dirbins
        currwind = f"d{cdi}_s{csp}"
        currwindloc = matrix.columns.get_loc(currwind)
        if not first:    
            matrix.loc[currwindloc, prevwind] += 1
        else:
            first = False
        prevwind = currwind
    matrix[matrix.columns] = (matrix[matrix.columns] / matrix[matrix.columns].sum())
    
    return matrix

def discretize(whole, height, dirs, speeds, do_markov = False):
    binned = bins(whole, height, dirs, speeds)
    histogram = histo(binned)
    if do_markov:
        m = markov(binned, histogram)
        return histogram, m
    return histogram, None


