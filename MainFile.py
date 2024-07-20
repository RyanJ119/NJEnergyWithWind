import EnergyClasses
import dailyValues
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import sys

dfDailyWindSpeeds=pd.read_csv("data/OnShoreWind/MesonetDataWithNumbersForDays.csv")
locationsOfMesonets = [dfDailyWindSpeeds['Lat'].unique(), dfDailyWindSpeeds['Lon'].unique()]
locationsOfMesonetsAsTuple = [(locationsOfMesonets[0][i], locationsOfMesonets[1][i]) for i in range(0, len(locationsOfMesonets[0]))]

year = 2023
if len(sys.argv) > 1: # Allow command-line year
    try:
        yr = int(sys.argv[1])
        if yr >= 2023:
            year = yr
    except:
        pass
print(year)
time_horizon = 360

### Here we initialize all current NJ energy producers as objects with a MWh Capacity
initialize_nuclear = [EnergyClasses.nuclear(1173), EnergyClasses.nuclear(2285)]

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
]

initialize_naturalGas = []
for i in naturalGasRatedMWH:
    initialize_naturalGas+=[EnergyClasses.natural_gas(5, i)]
    
   
    
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
]
initialize_biomass = []
for i in biomassRatedMWH:
    initialize_biomass+=[EnergyClasses.biomass(i)]
    
    

initialize_hydroelectric = [EnergyClasses.hydroelectric(10.95), EnergyClasses.hydroelectric(2.4)]
initialize_windfarms = [EnergyClasses.windfarmsOnShore(7.5,39.383621,-74.443047), EnergyClasses.windfarmsOnShore(1.5,40.668640,-74.116982)]

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
solarRatedMWH = [ # County-by-county
    86.084521 ,   # 1.  Sussex County
    125.964542,   # 2.  Warren County
    187.643747,   # 3.  Morris County
    133.264792,   # 4.  Hunterdon County
    209.362726,   # 5.  Somerset County
    113.437898,   # 6.  Passaic County
    220.747419,   # 7.  Bergen County
    141.283501,   # 8.  Hudson County
    162.533143,   # 9.  Essex County
    193.930024,   # 10. Union County
    624.221555,   # 11. Middlesex County
    271.952748,   # 12. Mercer County
    518.839100,   # 13. Burlington County
    322.405963,   # 14. Camden County
    236.375083,   # 15. Gloucester County
    77.505381 ,   # 16. Salem County
    378.554445,   # 17. Monmouth County
    412.859308,   # 18. Ocean County
    211.084045,   # 19. Atlantic County
    147.397675,   # 20. Cumberland County
    71.737073     # 21. Cape May County                    
]
initialize_solar = []
for i in range(len(solarRatedMWH)):
    initialize_solar+=[EnergyClasses.solar(i + 1, solarRatedMWH[i])]



############# Here we initialize Offshore wind in the same way. Future iterations will include the output of the spatial model here.
initialize_offshore=[EnergyClasses.offshoreWind(0)] 
   
############### Here we initialize our storage capacity which for now can be thought of as just one bucket we can pour energy into to use later


initialize_storage = EnergyClasses.storage(461)

############## here we bring in daily load data provided by DataMiner PJM 
dfTotalDailyLoad=pd.read_csv("data/PowerDemand/TotalNJLoadDaily.csv")
loadList = list(dfTotalDailyLoad['load'])
loadList = loadList[: len(loadList) - 7]

 ####### Here we estimate the daily energy produced by each type of energy producer. This code is written to maximize readability, but will be changed to speed up and for optimization routine       
energy_produced_nuclear = []
for i in range(time_horizon):
    energy_produced_nuclear+=[0]
    for j in initialize_nuclear:
        energy_produced_nuclear[-1] += j.powerProduced()
        
        
        
energy_produced_naturalGas  = []
for i in range(time_horizon):
    energy_produced_naturalGas +=[0]
    for j in initialize_naturalGas :
        energy_produced_naturalGas[-1] += j.powerProduced()
        
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
            print(windSpeed)
            energy_produced_windfarms[j]+=i.powerProduced(windSpeed)


# for i in range(time_horizon):
#     windSpeed = dailyValues.onshoreWindspeed(i)
#     energy_produced_windfarms +=[0]
#     for i in initialize_windfarms :
#         energy_produced_windfarms[-1] += i.powerProduced(windSpeed)




energy_produced_solar  = []
for i in range(time_horizon):
    # hoursOfSun = dailyValues.hoursOfSun()
    energy_produced_solar +=[0]
    for j in initialize_solar :
        energy_produced_solar[-1] += j.powerProduced(i)

energy_produced_offShore  = []
for i in range(time_horizon):
    windSpeed = dailyValues.offshoreWindspeed()
    energy_produced_offShore +=[0]
    for j in initialize_offshore :
        energy_produced_offShore[-1] += j.powerProduced(windSpeed)
        
netDailyEnergyGeneration=[sum(x) for x in zip(energy_produced_offShore,energy_produced_nuclear, energy_produced_naturalGas, energy_produced_biomass, energy_produced_hydroelectric, energy_produced_windfarms, energy_produced_solar)]

netDailyEnergy = [a_i - b_i for a_i, b_i in zip(netDailyEnergyGeneration, loadList)] 



print("the total energy deficit is: ", 1-(sum(netDailyEnergyGeneration)/sum(loadList)))


print("total Nuclear Energy Production = ", sum(energy_produced_nuclear))
print("total Onshore Wind Energy Production = ", sum(energy_produced_windfarms))
print("total Solar Energy Production = ", sum(energy_produced_solar))
print("total hydroelectric Energy Production = ", sum(energy_produced_hydroelectric))
print("total biomass Energy Production = ", sum(energy_produced_biomass))
print("total Natural Gas Energy Production = ", sum(energy_produced_naturalGas))


plt.plot(netDailyEnergy)
plt.show()


#### We estimate energy produced daily, energy consumed daily, and report results. A model will incorperate reactive components in an attempt to keep energy produced - energy consumed = 0



