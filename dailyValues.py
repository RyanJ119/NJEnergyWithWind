#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 10:45:30 2024

@author: ryanweightman
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import math
from datetime import datetime
import numpy as np



#The first day of this model is considered to be January 1 
def hoursOfSun():
  hours_of_sun=6
  standard_deviation = 1.5
  return np.random.normal(hours_of_sun, standard_deviation, 1)

def onshoreWindspeed(df, day, closest_mesonet):
  df = df[df['Lat']==closest_mesonet[0]]
  df = df[df['Date']==day]
  average_windspeed = df['DailyAvgWindSp'].mean()
  variance = df['DailyAvgWindSp'].var()
  return max(np.random.normal(average_windspeed, variance, 1),0)

def offshoreWindspeed():
  average_windspeed=22
  standard_deviation = 2
  
  return np.random.normal(average_windspeed, standard_deviation, 1)



def euclidean_distance(point1, point2):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(point1, point2)))

def closest_Mesonet(points, sample_point):
    closest = None
    min_distance = float('inf')
    
    for point in points:
        distance = euclidean_distance(point, sample_point)
        if distance < min_distance:
            min_distance = distance
            closest = point
    
    return closest