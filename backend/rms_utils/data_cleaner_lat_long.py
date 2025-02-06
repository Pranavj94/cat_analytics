
#############################################
### Imports 
#############################################
import pandas as pd
import numpy as np
import datetime
import re
import os
import requests
import json


#This function with handle lats and longs seperated by dashes..  
def _lat_scheme_1(x_in):
    try:
        x = x_in.replace('°','-')
    except:
        print(x_in)
        return x_in
    x = x.replace("'",'-')
    x = x.replace(' ','')
    x = x.replace('°','-')
    x = x.replace('"','')
    N = 'N' in x
    try:
        d, m, s = map(float, x[:-1].split('-'))
    except:
        return (x.split('-')[0])    
    lat = (d + m / 60. + s / 3600.) * (1 if N else -1)
    return lat


#This function with handle lats and longs seperated by dashes..  
def _long_scheme_1(x_in):
    try:
        x = x_in.replace('°','-')
    except:
        print(x_in)
        return x_in
    x = x.replace("'",'-')
    x = x.replace(' ','')
    x = x.replace('°','-')
    x = x.replace('"','')
    W = 'W' in x
    try:
        d, m, s = map(float, x[:-1].split('-'))
    except:
        return (x.split('-')[0])    
    long = (d + m / 60. + s / 3600.) * (-1 if W else 1)
    return long

#used when the schema is digital but with Letters and or degree symbols but no dashes
def _lat_scheme_2(x_in):
    try:
        x = x_in.replace('°','')
    except:
        return x_in

    if 'S' in x_in:
        x = x.replace('S','')
        x = -1*float(x)
    else:
        x = x.replace('N','')
        x = float(x)
    return x


#used when the schema is digital but with Letters and or degree symbols but no dashes
def _long_scheme_2(x_in):
    try:
        x = x_in.replace('°','')
    except:
        return x_in
    
    if 'W' in x_in:
        x = x.replace('W','')
        x = -1*float(x)
    else:
        x = x.replace('E','')
        x = float(x)
    return x


#using _ as the convetion to not import this externally
def _convert_long(x_in):
    clean_x = x_in
    
    #if a string that can be converted to a float, then convert it
    try:
        clean_x = float(clean_x)
    except:
        pass
    
    #if already a float return it
    if(isinstance(clean_x,float)):
        return str(clean_x)
        
    #call first schema if it contains more than one hyphon
    if(len(clean_x)>len(clean_x.replace('-',''))+1):
        return str(_long_scheme_1(clean_x))

    #call the second schema if it contains a degree symbol
    if(('°' in clean_x) or ('°' in clean_x)):
        return str(_long_scheme_2(clean_x))
    
    #else - return empty
    return ''

def _convert_lat(x_in):
    clean_x = x_in
    
    #if a string that can be converted to a float, then convert it
    try:
        clean_x = float(clean_x)
    except:
        pass
    
    #if already a float return it
    if(isinstance(clean_x,float)):
        return str(clean_x)
        
    #call first schema if it contains more than one hyphon
    if(len(clean_x)>len(clean_x.replace('-',''))+1):
        return str(_lat_scheme_1(clean_x))

    #call the second schema if it contains a degree symbol
    if(('°' in clean_x) or ('°' in clean_x)):
        return str(_lat_scheme_2(clean_x))
    
    #else - return empty
    return ''


def map_LATITUDE(values):
    return values.fillna('').apply(lambda x: _convert_lat(x))

def map_LONGITUDE(values):
    return values.fillna('').apply(lambda x: _convert_long(x))

    
