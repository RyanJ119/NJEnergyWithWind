import EnergyClasses
import dailyValues
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import sys

dfDailyWindSpeeds=pd.read_csv("data/OnShoreWind/MesonetDataWithNumbersForDays.csv")
locationsOfMesonets = [dfDailyWindSpeeds['Lat'].unique(), dfDailyWindSpeeds['Lon'].unique()]
locationsOfMesonetsAsTuple = [(locationsOfMesonets[0][i], locationsOfMesonets[1][i]) for i in range(0, len(locationsOfMesonets[0]))]

year = 2019
if len(sys.argv) > 1: # Allow command-line year
    try:
        yr = int(sys.argv[1])
        if yr >= 2024:
            year = yr
    except:
        pass
print(year)
time_horizon = 360

### Here we initialize all current NJ energy producers as objects with a MWh Capacity
initialize_nuclear = [EnergyClasses.nuclear(1173), EnergyClasses.nuclear(2285)];

naturalGasRatedMWH = [644
,1229
,168
,244
,294
,456
,974
,1566
,573
, 136
,705
,115
,67
,115
,823
,200
,315
,538
,740
,725
,81
];

initialize_naturalGas = []
# for i in naturalGasRatedMWH:
initialize_naturalGas+=[EnergyClasses.natural_gas(sum(naturalGasRatedMWH))]
    
   
    
biomassRatedMWH = [3.3
,7.0
,33.0
,9.1
,60.0
,12.0
,18.8
,13.8
,1.8
,1.8
,3.0
,37.5
,2.1
];
initialize_biomass = []
for i in biomassRatedMWH:
    initialize_biomass+=[EnergyClasses.biomass(i)];
    
    

initialize_hydroelectric = [EnergyClasses.hydroelectric(10.95), EnergyClasses.hydroelectric(2.4)];
initialize_windfarms = [EnergyClasses.windfarmsOnShore(7.5,39.383621,-74.443047), EnergyClasses.windfarmsOnShore(1.5,40.668640,-74.116982)];

# solarRatedMWH = [28.5
# ,27.3
# ,25.6
# ,23.5
# ,20.2
# ,19.9
# ,19.9
# ,16.5
# ,15.1
# ,14.1
# ,13.1
# ,13.0
# ,12.5
# ,12.0
# ,10.6
# ,10.1
# ,10.0
# ]
# solarRatedMWH = [ # County-by-county
#     86.084521 ,   # 1.  Sussex County
#     125.964542,   # 2.  Warren County
#     187.643747,   # 3.  Morris County
#     133.264792,   # 4.  Hunterdon County
#     209.362726,   # 5.  Somerset County
#     113.437898,   # 6.  Passaic County
#     220.747419,   # 7.  Bergen County
#     141.283501,   # 8.  Hudson County
#     162.533143,   # 9.  Essex County
#     193.930024,   # 10. Union County
#     624.221555,   # 11. Middlesex County
#     271.952748,   # 12. Mercer County
#     518.839100,   # 13. Burlington County
#     322.405963,   # 14. Camden County
#     236.375083,   # 15. Gloucester County
#     77.505381 ,   # 16. Salem County
#     378.554445,   # 17. Monmouth County
#     412.859308,   # 18. Ocean County
#     211.084045,   # 19. Atlantic County
#     147.397675,   # 20. Cumberland County
#     71.737073     # 21. Cape May County                    
# ]
initialize_solar = [EnergyClasses.solar(year=year)];



############# Here we initialize Offshore wind in the same way. Future iterations will include the output of the spatial model here.

   
def daily_wind_production(a0, a1, b1, aep_mwh, year=2025):
    """
    Compute daily production from a representative wind-speed year.

    Parameters
    ----------
    a0, a1, b1 : float
        Trigonometric coefficients for ws(d).
    aep_mwh : float
        Annual Energy Production (MWh/year).
    year : int
        Year for date index (non-leap).

    Returns
    -------
    df : pandas.DataFrame with columns:
        - date
        - dayofyear
        - ws          (daily wind speed)
        - production  (daily MWh, scaled to sum to AEP)
    """

    # 1. Compute daily wind speed
    t = np.arange(1, 366)
    ws = a0 + a1 * np.cos(2*np.pi*t/365) + b1 * np.sin(2*np.pi*t/365)

    # Make all speeds non-negative (if trig curve dips below zero)
    ws = np.maximum(ws, 0)

    # 2. Convert wind speed into relative power
    #    (just proportional to wind speed — simple model)
    rel_power = ws.copy()

    # 3. Scale so total = AEP
    scaling = aep_mwh / rel_power.sum()
    daily_prod = rel_power * scaling   # in MWh/day

    # 4. Build DataFrame
    dates = pd.date_range(f"{year}-01-01", periods=365, freq="D")

    return pd.DataFrame({
        "date": dates,
        "dayofyear": t,
        "ws": ws,
        "production": daily_prod
    })




# ---- load the two csvs ----
trig = pd.read_csv("opt/trig3_params_all_sites_heights.csv")
aep  = pd.read_csv("opt/optimized_AEP_all_farms_160m.csv")

# lease areas of interest
lease_ids = [532, 538, 541, 542, 549]

# keep only the trig rows for height 160 and desired lease areas
trig_160 = trig[(trig["height_m"] == 160) & (trig["lease_area"].isin(lease_ids))]

# merge in the optimized AEP (best_AEP) for those sites
merged = pd.merge(
    trig_160,
    aep[["lease_area", "best_AEP"]],
    on="lease_area",
    how="inner"
)

daily_by_lease = {}
all_daily = []

for _, row in merged.iterrows():
    lease = int(row["lease_area"])

    # ASSUMPTION: best_AEP is in GWh -> convert to MWh.
    # If best_AEP is already MWh, just remove the "* 1000".
    aep_mwh = row["best_AEP"] * 1000.0

    df_daily = daily_wind_production(
        a0=row["a0"],
        a1=row["a1"],
        b1=row["b1"],
        aep_mwh=aep_mwh,
        year=2025
    )

    df_daily["lease_area"] = lease
    df_daily["height_m"] = row["height_m"]

    daily_by_lease[lease] = df_daily
    all_daily.append(df_daily)

# optional: one big DataFrame with everything
all_daily = pd.concat(all_daily, ignore_index=True)

# examples:
df_0532 = daily_by_lease[532]
df_0538 = daily_by_lease[538]

total_daily_offshore_wind = all_daily.groupby("date")["production"].sum()
############### Here we initialize our storage capacity which for now can be thought of as just one bucket we can pour energy into to use later


initialize_storage = EnergyClasses.storage(461);

############## here we bring in daily load data provided by DataMiner PJM 
dfTotalDailyLoad=pd.read_csv("data/PowerDemand/TotalNJLoadDaily.csv");
loadList = list(dfTotalDailyLoad['load']);
loadList = loadList[: len(loadList) - 7];

 ####### Here we estimate the daily energy produced by each type of energy producer. This code is written to maximize readability, but will be changed to speed up and for optimization routine       
energy_produced_nuclear = []
for i in range(time_horizon):
    energy_produced_nuclear+=[0];
    for j in initialize_nuclear:
        energy_produced_nuclear[-1] += j.powerProduced()
        
energy_produced_biomass  = []
for i in range(time_horizon):
    energy_produced_biomass +=[0]
    for j in initialize_biomass :
        energy_produced_biomass[-1] += j.powerProduced()
        
energy_produced_hydroelectric  = []
for i in range(time_horizon):
    energy_produced_hydroelectric +=[0]
    for j in initialize_hydroelectric :
        energy_produced_hydroelectric[-1] += j.powerProduced()

energy_produced_windfarms  = [0]*365
for i in initialize_windfarms :
        closest_mesonet = dailyValues.closest_Mesonet(locationsOfMesonetsAsTuple, [i.lat,i.lon])
        for j in range(time_horizon):

            windSpeed = dailyValues.onshoreWindspeed(dfDailyWindSpeeds, j+1, closest_mesonet)
            #print(windSpeed);
            energy_produced_windfarms[j]+=i.powerProduced(windSpeed)


# for i in range(time_horizon):
#     windSpeed = dailyValues.onshoreWindspeed(i)
#     energy_produced_windfarms +=[0]
#     for i in initialize_windfarms :
#         energy_produced_windfarms[-1] += i.powerProduced(windSpeed)




energy_produced_solar  = []
gas_error_induced_by_solar  = []
for i in range(time_horizon):
    # hoursOfSun = dailyValues.hoursOfSun()
    energy_produced_solar +=[0]
    gas_error_induced_by_solar +=[0]
    for j in initialize_solar :
        energy_produced_solar[-1] += j.powerProduced(i)
        gas_error_induced_by_solar[-1] += j.errorProducedLatest()

#energy_produced_offShore  = []
# for i in range(time_horizon):
#     windSpeed = dailyValues.offshoreWindspeed()
#     energy_produced_offShore +=[0]
#     for j in initialize_offshore :
#         energy_produced_offShore[-1] += j.powerProduced(windSpeed)

pregas_gen =[sum(x) for x in zip(energy_produced_nuclear, energy_produced_biomass, energy_produced_hydroelectric, energy_produced_windfarms, energy_produced_solar)]

pregas_net = [a_i - b_i for a_i, b_i in zip(pregas_gen, loadList)] 

energy_produced_naturalGas  = []
for i in range(time_horizon):
    energy_produced_naturalGas +=[0]
    for j in initialize_naturalGas :
        energy_produced_naturalGas[-1] += j.powerProduced(-pregas_net[i], gas_error_induced_by_solar[i])
        
netDailyEnergyGeneration=[sum(x) for x in zip(total_daily_offshore_wind,energy_produced_nuclear, energy_produced_naturalGas, energy_produced_biomass, energy_produced_hydroelectric, energy_produced_windfarms, energy_produced_solar)]

netDailyEnergy = [a_i - b_i for a_i, b_i in zip(netDailyEnergyGeneration, loadList)] 



print("the total energy deficit is: ", 1-(sum(netDailyEnergyGeneration)/sum(loadList)))


print("total Nuclear Energy Production = ", sum(energy_produced_nuclear))
print("total Onshore Wind Energy Production = ", sum(energy_produced_windfarms))
print("total Solar Energy Production = ", sum(energy_produced_solar))
print("total hydroelectric Energy Production = ", sum(energy_produced_hydroelectric))
print("total biomass Energy Production = ", sum(energy_produced_biomass))
print("total Natural Gas Energy Production = ", sum(energy_produced_naturalGas))
print("total Offshore Wind Production = ", sum(total_daily_offshore_wind))
print("total Energy Production = ", sum(total_daily_offshore_wind)+sum(energy_produced_nuclear)+sum(energy_produced_windfarms)+sum(energy_produced_solar)+sum(energy_produced_hydroelectric)+sum(energy_produced_biomass)+sum(energy_produced_naturalGas))
#plt.plot(energy_produced_naturalGas)
plt.plot(netDailyEnergy, label="Net Daily Energy Production - Consumption")
#plt.plot(total_daily_offshore_wind)
plt.legend()
plt.show()


#### We estimate energy produced daily, energy consumed daily, and report results. A model will incorperate reactive components in an attempt to keep energy produced - energy consumed = 0



