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
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
        self.capacity_factor = .33
    
    def powerProduced(self, averageWindspeed):
        return self.ratedMWH*averageWindspeed
        
class solar:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
        self.capacity_factor = .33
    
    def powerProduced(self, hoursOfSun):
        return self.ratedMWH*hoursOfSun
        
        
class offshoreWind:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
        
    def powerProduced(self, averageWindspeed):
        return self.ratedMWH*averageWindspeed
    
class storage:
    def __init__(self , ratedMWH):

        self.ratedMWH = ratedMWH
    
    
    
        

        
        