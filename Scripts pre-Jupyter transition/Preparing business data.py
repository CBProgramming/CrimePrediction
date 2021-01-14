import pandas as pd
import numpy as np
import math
import re
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from datetime import datetime
from shapely.geometry import Point, Polygon
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

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

def generate_neighborhood_polygons(df):
    neighborhoods = []
    num_neighborhoods = len(df.index)
    for x in range(0,num_neighborhoods):
        raw_polygon_data = df.iloc[x,1]
        neighborhood_polygon = generate_polygon(raw_polygon_data)
        neighborhood_name = df.iloc[x,2]
        neighborhood_tuple = (neighborhood_polygon,neighborhood_name)
        neighborhoods.append(neighborhood_tuple)
    return neighborhoods

def generate_polygon(raw_polygon_data):
    raw_polygon_data = raw_polygon_data[16:-3]
    coords = ''
    coords_list = []
    for char in raw_polygon_data:
        if char == ' ' or char == ',':
            if coords != '':
                coords_list.append(float(coords))
            coords = ''
        else:
            coords = coords+char
    coords_list.append(float(coords))
    x = 0
    tuple_list = []
    while x < len(coords_list):
        next_tuple = (coords_list[x+1],coords_list[x])
        tuple_list.append(next_tuple)
        x+=2
    polygon = Polygon(tuple_list)
    return polygon

def open_businesses():
    df = pd.read_csv('SF_registered_business_locations.csv')
    print("Business dataset opened.")
    return df



def drop_unnecessary_columns(df):
    df = df.drop(columns=['Analysis Neighborhoods','Current Supervisor Districts',
                          'Current Police Districts','SF Find Neighborhoods','Neighborhoods',
                          'LIC Code Description','LIC Code','Transient Occupancy Tax','Parking Tax',
                          'NAICS Code','Mail State','Mail City','Location Id','Business Account Number',
                          'Business Start Date','Business End Date','Ownership Name','Street Address',
                          'City','State','Source Zipcode','Mail Address','Mail Zipcode',
                          'Supervisor District','Business Corridor','NAICS Code Description'])
    return df

#adjusted crime dataset starts 01/01/2019, business closed one year prior to this are not required 
def drop_end_dates_before_2019(df):
    # give none closed businesses an arbitray future closure date
    df['Location End Date'] = df['Location End Date'].fillna('01/01/2030')
    #convert all date strings to datetime
    df['Location End Date'] = pd.to_datetime(df['Location End Date'])
    df = df[df['Location End Date'].dt.year > 2017]
    return df

def determine_neighborhood_by_geolocation(df, neighborhood_polygons,neighborhoods):
    #replace blank gps coords with arbitrary point a significant distance from san francisco, in the ocean
    df['Business Location'] = df['Business Location'].fillna('POINT (-120.0 30.00)')
    df['Business Location'] = df['Business Location'].str[7:-1]
    df[['Longitude','Latitude']] = df['Business Location'].str.split(" ", expand = True)
    df = convert_gps_to_neighborhood(df,neighborhood_polygons,neighborhoods)
    return df

def convert_gps_to_neighborhood(df,neighborhood_polygons,neighborhoods):
    df['Neighborhood'] = np.nan
    num_records = len(df.index)
    for business_num in range(0,num_records):
        df.iloc[business_num,7] = ''
        if df.iloc[business_num,4] == '-120.0 30.00':
            for neighborhood in neighborhoods:
                if df.iloc[business_num,3] == neighborhood:
                    df.iloc[business_num,7] = neighborhood
            if df.iloc[business_num,7] == '':
                df.iloc[business_num,7] = 'no gps'     
        else:
            shortest_distance = 999999999
            closest_neighborhood = ''
            latitude = float(df.iloc[business_num,6])
            longitude = float(df.iloc[business_num,5])
            point = Point(latitude,longitude)
            for poly_tuple in neighborhood_polygons:
                if poly_tuple[0].contains(point) or poly_tuple[0].touches(point):
                    df.iloc[business_num,7] = poly_tuple[1]
                    break
                else:
                    distance_to_neighborhood = point.distance(poly_tuple[0])
                    if distance_to_neighborhood < shortest_distance:
                        shortest_distance = distance_to_neighborhood
                        closest_neighborhood = poly_tuple[1]
            if df.iloc[business_num,7] == '':
                #if less than half a mile from a neighborhood polygon and sufficiently north to be san francisco
                if shortest_distance < 0.018 and latitude > 37.709126:
                    df.iloc[business_num,7] = closest_neighborhood
    df.reset_index(drop=True, inplace=True)
    df = df[df.Neighborhood != '']
    df = df[df.Neighborhood != 'no gps']
    return df

def cleanup_columns(df):
    df = df.drop(columns=['Neighborhoods - Analysis Boundaries','Business Location',
                          'Longitude','Latitude'])
    return df

df = open_neighborhoods()
neighborhoods = get_neighborhoods(df)
neighborhood_polygons = generate_neighborhood_polygons(df)
df = open_businesses()
df = drop_unnecessary_columns(df)
df = drop_end_dates_before_2019(df)
df = determine_neighborhood_by_geolocation(df, neighborhood_polygons,neighborhoods)
df = cleanup_columns(df)
df.to_csv('businesses_0.1.csv', index = False)
