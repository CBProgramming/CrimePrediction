import pandas as pd
import numpy as np
import math
import re
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta, date
from shapely.geometry import Point, Polygon
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
import copy

def open_neighborhoods():
    df = pd.read_csv('SF_neighborhoods.csv')
    print("Neighborhoods dataset opened.")
    return df

def get_neighborhoods(df):
    neighborhoods = []
    num_neighborhoods = len(df.index)
    for x in range(0,num_neighborhoods):
        neighborhoods.append(df.iloc[x,2])
    return neighborhoods

def open_businesses():
    df = pd.read_csv('businesses_0.1.csv')
    print("Business dataset opened.")
    return df

def get_closures_per_day_per_neighborhood(closures):
    closures['Closures'] = 1
    closures['Location End Date'] = pd.to_datetime(closures['Location End Date'])
    closures = closures[closures['Location End Date'].dt.year < 2021]
    closures = closures.groupby(['Location End Date','Neighborhood']).count()
    closures = closures.drop(columns=[ 'DBA Name','Location Start Date'])
    closures = closures.reset_index()
    return closures

def add_zero_closure_neighborhoods(closures, neighborhoods):
    new_rows = pd.DataFrame()
    num_records = len(closures.index)
    current_date = closures.iloc[0,0]
    zero_closure_neighborhoods = copy.deepcopy(neighborhoods)
    for record in range(0,num_records):
        while closures.iloc[record,0] != current_date:
            #print("No closures on",current_date)
            for neighborhood in zero_closure_neighborhoods:
                #print("Adding",neighborhood,"on",current_date)
                new_row = {'Location End Date' : current_date,
                                   'Neighborhood' : neighborhood,
                                   'Closures' : 0}
                new_rows = new_rows.append(new_row,ignore_index=True)
            current_date = current_date + timedelta(days=1)
        if closures.iloc[record,0] == current_date:
            #print("Closue on",current_date,"found on line",record)
            #print("Removing",closures.iloc[record,1])
            zero_closure_neighborhoods.remove(closures.iloc[record,1])
            if record != num_records-1:
                if closures.iloc[record+1,0] != current_date:
                    for neighborhood in zero_closure_neighborhoods:
                        new_row = {'Location End Date' : current_date,
                                   'Neighborhood' : neighborhood,
                                   'Closures' : 0}
                        new_rows = new_rows.append(new_row,ignore_index=True)
                    zero_closure_neighborhoods = copy.deepcopy(neighborhoods)
                    current_date = current_date + timedelta(days=1)
                    #print("date set to",current_date,"on line",record)
        if current_date == date (2020,11,12):
            break
    for neighborhood in zero_closure_neighborhoods:
        new_row = {'Location End Date' : current_date,
                    'Neighborhood' : neighborhood,
                    'Closures' : 0}
        new_rows = new_rows.append(new_row,ignore_index=True)
    frames = [closures,new_rows]
    new_record = pd.concat(frames)
    new_record = new_record.sort_values(['Location End Date','Neighborhood'])
    return new_record

def shift_closures(closures,num_days):
    transitional_data = closures.shift(periods=(117*num_days))
    transitional_data = transitional_data['Closures']
    return transitional_data

def get_last_14_days_closures(closures):
    transitional_data = closures.shift(periods=(117*7))
    transitional_data = transitional_data['Last 7 days closures']
    return transitional_data

def get_last_28_days_closures(closures):
    transitional_data = closures.shift(periods=(117*14))
    transitional_data = transitional_data['Last 14 days closures']
    return transitional_data

def generate_new_closure_date_data(closures):
    closures['Closures 1 day ago'] = shift_closures(closures,1)
    closures['Closures 2 days ago'] = shift_closures(closures,2)
    closures['Closures 3 days ago'] = shift_closures(closures,3)
    closures['Closures 4 days ago'] = shift_closures(closures,4)
    closures['Closures 5 days ago'] = shift_closures(closures,5)
    closures['Closures 6 days ago'] = shift_closures(closures,6)
    closures['Closures 7 days ago'] = shift_closures(closures,7)
    closures['Closures 14 days ago'] = shift_closures(closures,14)
    closures['Closures 30 days ago'] = shift_closures(closures,30)
    closures['Closures 365 days ago'] = shift_closures(closures,365)
    closures['Last 7 days closures'] = (closures['Closures 1 day ago']
                                        + closures['Closures 2 days ago']
                                        + closures['Closures 3 days ago']
                                        + closures['Closures 4 days ago']
                                        + closures['Closures 5 days ago']
                                        + closures['Closures 6 days ago']
                                        + closures['Closures 7 days ago'])
    closures['Last 14 days closures'] = (closures['Last 7 days closures']
                                         + get_last_14_days_closures(closures))
    closures['Last 28 days closures'] = (closures['Last 14 days closures']
                                         + get_last_28_days_closures(closures))
    closures = closures.dropna()
    closures = closures[closures['Location End Date'].dt.year > 2018]
    closures = closures[closures['Location End Date'] <= '11-11-2020']
    #closures = closures[closures[pd.to_datetime(closures['Location End Date'])] < date (2020,11,12)] #final date of SFPD data
    return closures

def get_openings_per_day_per_neighborhood(openings):
    openings['Openings'] = 1
    openings['Location Start Date'] = pd.to_datetime(openings['Location Start Date'])
    openings = openings[openings['Location Start Date'].dt.year > 2017]
    openings = openings.groupby(['Location Start Date','Neighborhood']).count()
    openings = openings.drop(columns=[ 'DBA Name','Location End Date'])
    openings = openings.reset_index()
    return openings

def add_zero_opening_neighborhoods(openings, neighborhoods):
    new_rows = pd.DataFrame()
    num_records = len(openings.index)
    current_date = openings.iloc[0,0]
    zero_opening_neighborhoods = copy.deepcopy(neighborhoods)
    for record in range(0,num_records):
        while openings.iloc[record,0] != current_date:
            #print("No openings on",current_date)
            for neighborhood in zero_opening_neighborhoods:
                #print("Adding",neighborhood,"on",current_date)
                new_row = {'Location Start Date' : current_date,
                                   'Neighborhood' : neighborhood,
                                   'Openings' : 0}
                new_rows = new_rows.append(new_row,ignore_index=True)
            current_date = current_date + timedelta(days=1)
        if openings.iloc[record,0] == current_date:
            zero_opening_neighborhoods.remove(openings.iloc[record,1])
            if record != num_records-1:
                if openings.iloc[record+1,0] != current_date:
                    for neighborhood in zero_opening_neighborhoods:
                        new_row = {'Location Start Date' : current_date,
                                   'Neighborhood' : neighborhood,
                                   'Openings' : 0}
                        new_rows = new_rows.append(new_row,ignore_index=True)
                    zero_opening_neighborhoods = copy.deepcopy(neighborhoods)
                    current_date = current_date + timedelta(days=1)
        if current_date == date (2020,11,12):
            break
    for neighborhood in zero_opening_neighborhoods:
        new_row = {'Location Start Date' : current_date,
                    'Neighborhood' : neighborhood,
                    'Openings' : 0}
        new_rows = new_rows.append(new_row,ignore_index=True)
    frames = [openings,new_rows]
    new_record = pd.concat(frames)
    new_record = new_record.sort_values(['Location Start Date','Neighborhood'])
    return new_record

def shift_openings(openings,num_days):
    transitional_data = openings.shift(periods=(117*num_days))
    transitional_data = transitional_data['Openings']
    return transitional_data

def get_last_14_days_openings(openings):
    transitional_data = openings.shift(periods=(117*7))
    transitional_data = transitional_data['Last 7 days openings']
    return transitional_data

def get_last_28_days_openings(openings):
    transitional_data = openings.shift(periods=(117*14))
    transitional_data = transitional_data['Last 14 days openings']
    return transitional_data

def generate_new_opening_date_data(openings):
    openings['Openings 1 day ago'] = shift_openings(openings,1)
    openings['Openings 2 days ago'] = shift_openings(openings,2)
    openings['Openings 3 days ago'] = shift_openings(openings,3)
    openings['Openings 4 days ago'] = shift_openings(openings,4)
    openings['Openings 5 days ago'] = shift_openings(openings,5)
    openings['Openings 6 days ago'] = shift_openings(openings,6)
    openings['Openings 7 days ago'] = shift_openings(openings,7)
    openings['Openings 14 days ago'] = shift_openings(openings,14)
    openings['Openings 30 days ago'] = shift_openings(openings,30)
    openings['Openings 365 days ago'] = shift_openings(openings,365)
    openings['Last 7 days openings'] = (openings['Openings 1 day ago']
                                        + openings['Openings 2 days ago']
                                        + openings['Openings 3 days ago']
                                        + openings['Openings 4 days ago']
                                        + openings['Openings 5 days ago']
                                        + openings['Openings 6 days ago']
                                        + openings['Openings 7 days ago'])
    openings['Last 14 days openings'] = (openings['Last 7 days openings']
                                         + get_last_14_days_openings(openings))
    openings['Last 28 days openings'] = (openings['Last 14 days openings']
                                         + get_last_28_days_openings(openings))
    openings = openings.dropna()
    openings = openings[openings['Location Start Date'].dt.year > 2018]
    openings = openings[openings['Location Start Date'] <= '11-11-2020']
    #openings = openings[openings[pd.to_datetime(openings['Location Start Date'])] < date (2020,11,12)] #final date of SFPD data
    return openings
    
df = open_neighborhoods()
neighborhoods = get_neighborhoods(df)
df = open_businesses()
closures = get_closures_per_day_per_neighborhood(df)
closures = add_zero_closure_neighborhoods(closures,neighborhoods)
closures = generate_new_closure_date_data(closures)
closures.to_csv('businesses_closures.csv', index = False)
df = open_businesses()
openings = get_openings_per_day_per_neighborhood(df)
openings = add_zero_opening_neighborhoods(openings,neighborhoods)
openings = generate_new_opening_date_data(openings)
openings.to_csv('businesses_openings.csv', index = False)
#closures.to_csv('businesses_closure_basic.csv', index = False)
