import pandas as pd
import urllib.parse
import time, os, re, requests, glob

FIRST_YEAR = 2020 # Minimum: 1998
LAST_YEAR = 2022 # Maximum: 2022

API_KEY = "APIKEY"
EMAIL = "EMAIL"
BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-2-2-download.csv?"

#   Each code in POINTS represents a point in the NSR database.
#   The point for each county comes from the averages of the
# coordinates of each ZIP code within that county, "weighted"
# by the total estimated solar panel size in that ZIP code.
#    This is a basic heuristic to bring each county's point closer
# to a single ZIP, should that ZIP contain a large majority of the
# county's solar output.

POINTS = [
    '1222098', # 1.  Sussex County
    '1210464', # 2.  Warren County
    '1227223', # 3.  Morris County
    '1214391', # 4.  Hunterdon County
    '1225952', # 5.  Somerset County
    '1237553', # 6.  Passaic County
    '1242678', # 7.  Bergen County
    '1241400', # 8.  Hudson County
    '1237557', # 9.  Essex County
    '1234973', # 10. Union County
    '1231092', # 11. Middlesex County
    '1223395', # 12. Mercer County
    '1219582', # 13. Burlington County
    '1211795', # 14. Camden County
    '1207862', # 15. Gloucester County
    '1201272', # 16. Salem County
    '1238849', # 17. Monmouth County
    '1237577', # 18. Ocean County
    '1224702', # 19. Atlantic County
    '1210498', # 20. Cumberland County
    '1218325'  # 21. Cape May County
]

def main():
    input_data = {
        'attributes': 'ghuv-280-400',
        'interval': '60',
        'to_utc': 'false',
        
        'api_key': API_KEY,
        'email': EMAIL,
    }

    if not os.path.exists("cache"):
        os.makedirs("cache")

    for name in (str(num) for num in range(FIRST_YEAR, LAST_YEAR + 1)):
        print(f"Processing name: {name}")
        county = 1
        for id, location_ids in enumerate(POINTS):
            input_data['names'] = [name]
            input_data['location_ids'] = location_ids
            print(f'Making request for point group {id + 1} of {len(POINTS)}...')

            fname = f"cache/{str(county)}_{name}.csv"

            if os.path.isfile(fname): # If the data in question is already cached, no need for more downloads
                print("Already cached!")
                continue

            if '.csv' in BASE_URL:
                url = BASE_URL + urllib.parse.urlencode(input_data, True)

                data = pd.read_csv(url)

                
                data.to_csv(fname, index=False)
                with open (fname, 'r') as f:
                    plain = f.read()
                    plain = re.sub(r'.*Year,Month,', r'Year,Month,', plain, count=1, flags = re.DOTALL)
                    plain = re.sub(r'Global Horizontal UV Irradiance \(280-400nm\)', r'Irradiance', plain, count = 1)
                    plain = re.sub(r',,', r'', plain)
                    with open (fname, 'w') as f2:
                        f2.write(plain)
                pd.read_csv(fname).drop(columns=["Minute", "Year"]).to_csv(fname, index=False)
                

                time.sleep(1)
            else:
                exit(1)
            county += 1
            print(f'Processed')

    # Merge downloaded data by county to get an average-irradiance-per-hour view
    frames = []

    for county in range(1, len(POINTS) + 1):
        files = glob.glob(f"cache/{str(county)}_*.csv")
        if len(files) == 0: exit(1);
        dfs = []
        for fname in files:
            dfs.append(pd.read_csv(fname))
        full = pd.concat(dfs)

        full['exact_hour'] = list(zip(full['Month'], full['Day'], full['Hour']))
        full = full.groupby("exact_hour", as_index=False).agg({'Month':'median', 'Day':'median', 'Hour': 'median', 'Irradiance': 'mean'})
        full['Month'] = full['Month'].astype(int)
        full['Day'] = full['Day'].astype(int)
        full['Hour'] = full['Hour'].astype(int)
        full = full.drop(columns=["exact_hour"])
        frames.append(full)

        full.to_csv(f"points/{str(county)}.csv", index=False)

    # Find a high level of irradiance that we will (quite generously) assume induces maximum solar output
    normalization = pd.concat(frames, ignore_index=True)
    normalization['exact_day'] = list(zip(normalization['Month'], normalization['Day']))
    high = normalization.groupby("exact_day", as_index=False).max().drop(columns=["exact_day"]).quantile(q = 0.95)["Irradiance"]

    # Normalize irradiance with the found high value; then make a daily 'sum' to multiply grid size by
    for county in range(1, len(POINTS) + 1):
        full = pd.read_csv(f"points/{str(county)}.csv")

        full['Irradiance'] = full['Irradiance'].apply(lambda x : min(x / high, 1.0))
        full['exact_day'] = list(zip(full['Month'], full['Day']))
        full = full.groupby("exact_day", as_index=False).agg({'Month':'median', 'Day':'median', 'Hour': 'median', 'Irradiance': 'sum'})
        full = full.drop(columns=["exact_day", "Hour", "Day", "Month"])

        full.to_csv(f"points/{str(county)}.csv", index=False)

def get_response_json_and_handle_errors(response: requests.Response) -> dict:
    """Takes the given response and handles any errors, along with providing
    the resulting json

    Parameters
    ----------
    response : requests.Response
        The response object

    Returns
    -------
    dict
        The resulting json
    """
    if response.status_code != 200:
        print(f"An error has occurred with the server or the request. The request response code/status: {response.status_code} {response.reason}")
        print(f"The response body: {response.text}")
        exit(1)

    try:
        response_json = response.json()
    except:
        print(f"The response couldn't be parsed as JSON, likely an issue with the server, here is the text: {response.text}")
        exit(1)

    if len(response_json['errors']) > 0:
        errors = '\n'.join(response_json['errors'])
        print(f"The request errored out, here are the errors: {errors}")
        exit(1)
    return response_json

if __name__ == "__main__":
    main()