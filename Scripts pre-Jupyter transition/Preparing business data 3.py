import pandas as pd
import numpy as np
import math
import re
from datetime import date, datetime, timedelta

def open_businesses():
    df = pd.read_csv('businesses_0.2.csv')
    print("Business dataset opened.")
    return df

def shift_days(df,num_days):
    transitional_data = df.shift(periods=(117*num_days))
    transitional_data = transitional_data['Number of businesses']
    return transitional_data

def get_last_14_days(df):
    transitional_data = df.shift(periods=(117*7))
    transitional_data = transitional_data['Last 7 days']
    return transitional_data

def get_last_28_days(df):
    transitional_data = df.shift(periods=(117*14))
    transitional_data = transitional_data['Last 14 days']
    return transitional_data

def generate_new_date_data(df):
    df['Businesses 1 day ago'] = shift_days(df,1)
    df['Businesses 2 days ago'] = shift_days(df,2)
    df['Businesses 3 days ago'] = shift_days(df,3)
    df['Businesses 4 days ago'] = shift_days(df,4)
    df['Businesses 5 days ago'] = shift_days(df,5)
    df['Businesses 6 days ago'] = shift_days(df,6)
    df['Businesses 7 days ago'] = shift_days(df,7)
    df['Businesses 14 days ago'] = shift_days(df,14)
    df['Businesses 30 days ago'] = shift_days(df,30)
    df['Businesses 365 days ago'] = shift_days(df,365)
    df = df.dropna()
    return df

df = open_businesses()
df = generate_new_date_data(df)
df.to_csv('businesses_0.3.csv', index = False)
