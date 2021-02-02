import pandas as pd
import math
import numpy as np
from shapely.geometry import Point, Polygon
import copy
import time
import re
from datetime import date, datetime, timedelta
from shapely.geometry import Point, Polygon
import copy
from sklearn.preprocessing import LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import make_column_transformer

neighbourhood_data_name = "SF_neighborhoods.csv"
sfpd_data_name = "incidents_new_data.csv" #current range 12/11/2020 to 28/01/2021
business_data_name = "business_new_data.csv"
final_data_name = "new_final_data.csv"
start_day = 18
start_month = 11
start_year = 2020
end_day = 28
end_month = 1
end_year = 2021
start_date_string = str(start_year)+'-'+str(start_month)+'-'+str(start_day)
start_date = date(start_year,start_month,start_day)
one_year_before_start_date = start_date - timedelta(days=365)
end_date = date (end_year,end_month,end_day)
date_after_end_date = end_date + timedelta(days=1)
future_year_increment = 50
future_date = str(end_year+future_year_increment)+'-'+str(end_month)+'-'+str(end_day)
future_year = end_year + future_year_increment
business_start_date = str(start_month)+'-'+str(start_day)+'-'+str(start_year)
business_end_date = str(end_month)+'-'+str(end_day)+'-'+str(end_year)

def open_neighborhoods():
    df = pd.read_csv(neighbourhood_data_name)
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

df = open_neighborhoods()
neighborhoods = get_neighborhoods(df)
num_neighbourhoods = len(neighborhoods)
neighborhood_polygons = generate_neighborhood_polygons(df)

def add_missing_neighborhoods(business_df):
    new_rows = pd.DataFrame()
    num_records = len(business_df.index)
    current_date = start_date
    zero_business_neighborhoods = copy.deepcopy(neighborhoods)
    while current_date <= end_date:
        print(current_date)
        data = business_df.loc[business_df['Date'].str.contains(str(current_date))]
        #print(data.head())
        for neighborhood in neighborhoods:
            if neighborhood not in data['Neighborhood'].tolist():
                print(neighborhood)
                new_row = {'Date' : current_date,
                               'Neighborhood' : neighborhood,
                               'Number of businesses' : 0}
                new_rows = new_rows.append(new_row,ignore_index=True)
        current_date += timedelta(days=1)
    frames = [business_df,new_rows]
    new_record = pd.concat(frames)
    new_record.reset_index(drop=True, inplace=True)
    return new_record

business_df = pd.read_csv("bus_progress5.csv")
business_df = add_missing_neighborhoods(business_df)
business_df.to_csv("bus_progress5555555555.csv", index = True)
