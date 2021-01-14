import pandas as pd
import numpy as np
import math
import re
from datetime import date, datetime, timedelta
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

def calculate_new_businesses(df):
    df['Location Start Date'] = pd.to_datetime(df['Location Start Date'])
    df = df[df['Location Start Date'].dt.year > 2017]
    df['New businesses'] = 1
    df = df.groupby(['Location Start Date','Neighborhood']).count()
    df = df.reset_index()
    return df

def check_for_missing_neighborhoods_business_openings(df,neighborhoods):
    new_rows = pd.DataFrame()
    num_records = len(df.index)
    current_date = df.iloc[0,0]
    zero_business_opening_neighborhoods = copy.deepcopy(neighborhoods)
    for record in range(0,num_records):
        zero_business_opening_neighborhoods.remove(df.iloc[record,1])
        if record != num_records-1:
            if df.iloc[record+1,0] != current_date:
                for neighborhood in zero_business_opening_neighborhoods:
                    new_row = {'Location Start Date' : current_date,
                               'Neighborhood' : neighborhood,
                               'New businesses' : 0}
                    new_rows = new_rows.append(new_row,ignore_index=True)
                zero_business_opening_neighborhoods = copy.deepcopy(neighborhoods)
                current_date = df.iloc[record+1,0]
    for neighborhood in zero_business_opening_neighborhoods:
        new_row = {'Location Start Date' : current_date,
                    'Neighborhood' : neighborhood,
                    'New businesses' : 0}
        new_rows = new_rows.append(new_row,ignore_index=True)
    frames = [df,new_rows]
    new_record = pd.concat(frames)
    new_record = new_record.sort_values(['Location Start Date','Neighborhood'])
    new_record = new_record.drop(columns=['DBA Name','Location End Date'])
    return new_record

def calculate_closed_businesses(df):
    df['Location End Date'] = pd.to_datetime(df['Location End Date'])
    df = df[df['Location End Date'].dt.year > 2017]
    df['Closed businesses'] = 1
    df = df.groupby(['Location End Date','Neighborhood']).count()
    df = df.reset_index()
    return df

def check_for_missing_neighborhoods_business_closures(df,neighborhoods):
    new_rows = pd.DataFrame()
    num_records = len(df.index)
    current_date = df.iloc[0,0]
    zero_business_closure_neighborhoods = copy.deepcopy(neighborhoods)
    for record in range(0,num_records):
        zero_business_closure_neighborhoods.remove(df.iloc[record,1])
        if record != num_records-1:
            if df.iloc[record+1,0] != current_date:
                for neighborhood in zero_business_closure_neighborhoods:
                    new_row = {'Location End Date' : current_date,
                               'Neighborhood' : neighborhood,
                               'Closed businesses' : 0}
                    new_rows = new_rows.append(new_row,ignore_index=True)
                zero_business_closure_neighborhoods = copy.deepcopy(neighborhoods)
                current_date = df.iloc[record+1,0]
    for neighborhood in zero_business_closure_neighborhoods:
        new_row = {'Location End Date' : current_date,
                    'Neighborhood' : neighborhood,
                    'Closed businesses' : 0}
        new_rows = new_rows.append(new_row,ignore_index=True)
    frames = [df,new_rows]
    new_record = pd.concat(frames)
    new_record = new_record.sort_values(['Location End Date','Neighborhood'])
    new_record = new_record.drop(columns=['DBA Name','Location Start Date'])
    return new_record

def combine_data(new_bus_df,closed_bus_df):
    new_bus_df = new_bus_df.reset_index()
    closed_bus_df = closed_bus_df.reset_index()
    new_bus_df['Closed businesses'] = closed_bus_df['Closed businesses']
    #closed_bus_df = closed_bus_df.drop(columns=[ 'Location End Date','Neighborhood'])
    #combined_open_close_data = pd.concat([new_bus_df, closed_bus_df], ignore_index=True, sort=False)
    return new_bus_df

df = open_neighborhoods()
neighborhoods = get_neighborhoods(df)
df = open_businesses()
new_bus_df = calculate_new_businesses(df)
new_bus_df = check_for_missing_neighborhoods_business_openings(new_bus_df,neighborhoods)
closed_bus_df = calculate_closed_businesses(df)
closed_bus_df = check_for_missing_neighborhoods_business_closures(closed_bus_df,neighborhoods)
combined_open_close_data = combine_data(new_bus_df,closed_bus_df)
combined_open_close_data.to_csv('new and closed businesses.csv', index = False)
