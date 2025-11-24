from helpers import downloader, outliner, discretizer
import pandas as pd
import numpy as np
from pathlib import Path
import sys

STARTYEAR, ENDYEAR = 2015, 2023
MALFORMED_SITES_ERROR = "Delete all subfolders in 'sites' besides 'define' and try again."

if len(sys.argv) < 3:
    DIRECTIONS = 16
    SPEEDS = 9
else:
    DIRECTIONS = sys.argv[1]
    SPEEDS = sys.argv[2]

def unmade(d: Path):
    if not d.is_file():
        if d.is_dir(): sys.exit(MALFORMED_SITES_ERROR)
        return True
    return False
    
areas = pd.read_csv("sites/define/areas.csv")
for row in areas.itertuples(index = False):
    directory = Path(f"sites/{row.num}")
    if not directory.is_dir():
        if directory.is_file(): sys.exit(MALFORMED_SITES_ERROR)
        directory.mkdir()

    boundary_npy = directory / "boundary.npy"
    if unmade(boundary_npy):
        np.save(boundary_npy, outliner.outline(f"sites/define/{row.num}.png"))
    else:
        np.load(boundary_npy)
    
    whole_csv = directory / "whole.csv"
    if unmade(whole_csv):
        print(f"Downloading {row.num}", end="")
        whole = downloader.download_all(STARTYEAR, ENDYEAR, row.long, row.lat)
        whole.to_csv(whole_csv)
    else:
        print(f"Already downloaded: {row.num}", end="")
        whole = pd.read_csv(whole_csv)

    for h in [10] + list(range(20, 201, 20)):
        print(whole)
        print(h)
        histo_csv = directory / f"histo_{h}.csv"
        # markov_csv = directory / f"markov_{h}.csv"
        if unmade(histo_csv):
            his, _ = discretizer.discretize(whole, h, DIRECTIONS, SPEEDS, False)
            his.to_csv(histo_csv)
            # m.to_csv(markov_csv)