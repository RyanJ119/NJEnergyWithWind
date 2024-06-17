import EnergyClasses
import dailyValues
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

time_horizon = 360
### Here we initialize all NJ energy producers as objects producing energy over time
initialize_nuclear = [EnergyClasses.nuclear(1173), EnergyClasses.nuclear(2285)]

naturalGasRatedMWH = [644
,1229
,168
,244
,294
,456
,974
,1566
,573, 136
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
initialize_windfarms = [EnergyClasses.windfarmsOnShore(7.5), EnergyClasses.windfarmsOnShore(1.5)]

solarRatedMWH = [28.5
,27.3
,25.6
,23.5
,20.2
,19.9
,19.9
,16.5
,15.1
,14.1
,13.1
,13.0
,12.5
,12.0
,10.6
,10.1
,10.0
]
initialize_solar = []
for i in solarRatedMWH:
    initialize_solar+=[EnergyClasses.solar(i)]


initialize_offshore=[EnergyClasses.offshoreWind(0)] 
   
############### Here we initialize our storage capacity which for now can be thought of as just one bucket we can pour energy into to use later


initialize_storage = EnergyClasses.storage(461)

############## here we bring in daily load data provided by DataMiner PJM 
dfTotalDailyLoad=pd.read_csv("data/TotalNJLoadDaily.csv")
loadList = list(dfTotalDailyLoad['load'])
loadList = loadList[: len(loadList) - 7]

 ####### Here we estimate the daily energy produced by each type of energy producer       
energy_produced_nuclear = []
for i in range(time_horizon):
    energy_produced_nuclear+=[0]
    for i in initialize_nuclear:
        energy_produced_nuclear[-1] += i.powerProduced()
        
        
        
energy_produced_naturalGas  = []
for i in range(time_horizon):
    energy_produced_naturalGas +=[0]
    for i in initialize_naturalGas :
        energy_produced_naturalGas[-1] += i.powerProduced()
        
energy_produced_biomass  = []
for i in range(time_horizon):
    energy_produced_biomass +=[0]
    for i in initialize_biomass :
        energy_produced_biomass[-1] += i.powerProduced()
        
energy_produced_hydroelectric  = []
for i in range(time_horizon):
    energy_produced_hydroelectric +=[0]
    for i in initialize_hydroelectric :
        energy_produced_hydroelectric[-1] += i.powerProduced()

energy_produced_windfarms  = []
for i in range(time_horizon):
    windSpeed = dailyValues.onshoreWindspeed()
    energy_produced_windfarms +=[0]
    for i in initialize_windfarms :
        energy_produced_windfarms[-1] += i.powerProduced(windSpeed)




energy_produced_solar  = []
for i in range(time_horizon):
    hoursOfSun = dailyValues.hoursOfSun()
    energy_produced_solar +=[0]
    for i in initialize_solar :
        energy_produced_solar[-1] += i.powerProduced(hoursOfSun)

energy_produced_offShore  = []
for i in range(time_horizon):
    windSpeed = dailyValues.offshoreWindspeed()
    energy_produced_offShore +=[0]
    for i in initialize_offshore :
        energy_produced_offShore[-1] += i.powerProduced(windSpeed)
        
netDailyEnergyGeneration=[sum(x) for x in zip(energy_produced_offShore,energy_produced_nuclear, energy_produced_naturalGas, energy_produced_biomass, energy_produced_hydroelectric, energy_produced_windfarms, energy_produced_solar)]

netDailyEnergy = [a_i - b_i for a_i, b_i in zip(netDailyEnergyGeneration, loadList)] 



print("the total energy deficit is: ", 1-(sum(netDailyEnergyGeneration)/sum(loadList)))


print("total Nuclear Energy Production = ", sum(energy_produced_nuclear))
print("total Solar Energy Production = ", sum(energy_produced_solar))
print("total hydroelectric Energy Production = ", sum(energy_produced_hydroelectric))
print("total biomass Energy Production = ", sum(energy_produced_biomass))
print("total Natural Gas Energy Production = ", sum(energy_produced_naturalGas))


plt.plot(netDailyEnergy)
plt.show()






