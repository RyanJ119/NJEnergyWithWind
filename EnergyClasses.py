#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 10:43:13 2024

@author: ryanweightman
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 10:28:42 2024

@author: ryanweightman
"""
import pandas as pd
import os, random
import numpy as np



class nuclear:
    def __init__(self, ratedMWH):
        self.ratedMWH = ratedMWH
        self.capacity_factor = .9
        
    def powerProduced(self):
        return self.ratedMWH*24*self.capacity_factor
        
    
class natural_gas:
    # def __init__(self, refillSchedule , ratedMWH):
    #     self.refillSchedule =  refillSchedule
    #     self.ratedMWH = ratedMWH
    #     self.capacity_factor = .33

    def __init__(self, ratedMWH):
        self.ratedMWH = ratedMWH
        self.demand_error_rel = 0.02

    def powerProduced(self, demand, ext_error):
        resp = demand + ext_error
        resp = resp - resp * self.demand_error_rel + resp * self.demand_error_rel * 2 * random.random()
        if resp <= 0: return 0.0;
        return min(self.ratedMWH * 24, resp)
    
    # def powerProduced(self):
    #     return self.ratedMWH*24*self.capacity_factor
    
    
    
class biomass:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
        self.capacity_factor = .33
    
    def powerProduced(self):
        return self.ratedMWH*24*self.capacity_factor
    
        
        
class hydroelectric:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
        self.capacity_factor = .33
    
    def powerProduced(self):
        return self.ratedMWH*24*self.capacity_factor
        
    
    
    
    
    
class windfarmsOnShore:
    def __init__(self , ratedMWH, lat, lon):

        self.ratedMWH = ratedMWH
        self.capacity_factor = .33
        self.lat = lat
        self.lon = lon
    
    
    
    
    
    
    
    def powerProduced(self, averageWindspeed):
        return self.ratedMWH*averageWindspeed
        
class solar:
    def __init__(self , year):
        self.jancapacity = 4779385 + (year - 2024) * 425000
        self.solid_latest = 0
        self.varied_latest = 0

        cf = "data/solar/monthlyratio.csv"
        if os.path.isfile(cf):
            self.ratio = pd.read_csv(cf)
            self.basic = False
        else:
            exit(1)
  
    def powerProduced(self, day):
        day_ratio = ((30 - (day % 30)) * self.ratio['ratio'][day // 30] + (day % 30) * self.ratio['ratio'][((day // 30) + 1) % 12]) / 30 / 30
        solid_produced = (self.jancapacity + day * 1180) * day_ratio
        varied_produced = solid_produced - solid_produced * .05 + solid_produced * .1 * random.random()

        self.solid_latest = solid_produced
        self.varied_latest = varied_produced

        return varied_produced

    def errorProducedLatest(self):
        return self.solid_latest - self.varied_latest
        
        


class OffshoreWind:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
        
    def powerProduced(self, averageWindspeed):
        return self.ratedMWH*averageWindspeed
        
    
class storage:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
    
    
    
        

        
        