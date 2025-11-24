import pandas as pd
import urllib

URL = f"http://developer.nrel.gov/api/wind-toolkit/v2/wind/wtk-bchrrr-v1-0-0-download.csv?"

ATTRS = "winddirection_10m,windspeed_10m"
for x in range(20, 201, 20):
    ATTRS += f",winddirection_{x}m,windspeed_{x}m"

with open("api_key") as f: API_KEY, EMAIL = f.read().splitlines()

def download_year(year, long, lat):
    input_data = {
        'attributes': ATTRS,
        'interval': '60',
        'api_key': API_KEY,
        'email': EMAIL,
        'names': year,
        'wkt': f"POINT({long} {lat})"
    }

    url_data = URL + urllib.parse.urlencode(input_data, True)
    return pd.read_csv(url_data, skiprows = 1)

def download_all(startyear, endyear, long, lat):
    print(f"Download started for {{lat: {lat}, long: {long}}}, years [{startyear}, {endyear}]")
    dfs = []
    for y in range(startyear, endyear + 1):
        dy = download_year(y, long, lat)
        dfs.append(dy)
        print(".", end="")
    return pd.concat(dfs, ignore_index=True) # Concatenated dataframe for all years