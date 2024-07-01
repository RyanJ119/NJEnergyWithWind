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
import os

class nuclear:
    def __init__(self, ratedMWH):
        self.ratedMWH = ratedMWH
        self.capacity_factor = .9
        
    def powerProduced(self):
        return self.ratedMWH*24*self.capacity_factor
        
    
class natural_gas:
    def __init__(self, refillSchedule , ratedMWH):
        self.refillSchedule =  refillSchedule
        self.ratedMWH = ratedMWH
        self.capacity_factor = .33
    
    def powerProduced(self):
        return self.ratedMWH*24*self.capacity_factor
    
    
    
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
    def __init__(self , county, ratedMWH):
        cf = f"data/solar/points/{county}.csv"
        if os.path.isfile(cf):
            self.truncations = pd.read_csv(cf)
            self.basic = False
        else:
            self.basic = True
        self.ratedMWH = ratedMWH
        self.capacity_factor = .33
    
    def powerProduced(self, day):
        if self.basic: return self.ratedMWH*self.capacity_factor
        else: return self.ratedMWH*self.truncations.iat[day, 0]
        
        
class offshoreWind:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
        
    def powerProduced(self, averageWindspeed):
        return self.ratedMWH*averageWindspeed
    
class storage:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
    
    
    
        

        
        