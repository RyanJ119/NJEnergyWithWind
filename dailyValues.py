#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 10:45:30 2024

@author: ryanweightman
"""
import numpy as np


#The first day of this model is considered to be January 1 
def hoursOfSun():
  hours_of_sun=6
  standard_deviation = 1.5
  return np.random.normal(hours_of_sun, standard_deviation, 1)

def onshoreWindspeed():
  average_windspeed=9
  standard_deviation = 4
  
  return np.random.normal(average_windspeed, standard_deviation, 1)

def offshoreWindspeed():
  average_windspeed=22
  standard_deviation = 2
  
  return np.random.normal(average_windspeed, standard_deviation, 1)