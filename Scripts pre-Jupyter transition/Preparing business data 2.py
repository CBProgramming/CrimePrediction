import pandas as pd
import numpy as np
import math
import re
from datetime import date, datetime, timedelta


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

def generate_dates_for_each_business(df):
    df['Date'] = np.nan
    df['Date']= pd.to_datetime(df['Date'])
    df['Location Start Date']= pd.to_datetime(df['Location Start Date'])
    df['Location End Date']= pd.to_datetime(df['Location End Date'])
    new_df = pd.DataFrame()
    final_df = pd.DataFrame()
    num_records = len(df.index)
    current_date = datetime(2018, 7, 1) #one year prior to beginning of SFPD data
    end_date = datetime(2020, 11, 11) #final date of SFPD data
    delta = timedelta(days = 1)
    while current_date <= end_date:
        print (current_date.strftime("%Y-%m-%d"))
        num_records = len(df.index)
        new_df = (df.loc[(df['Location Start Date'] <= current_date) & (current_date < df['Location End Date'])])
        new_df['Date'] = current_date
        final_df = pd.concat((new_df,final_df))
        current_date += delta
    final_df['Number of businesses'] = 1
    final_df = final_df.groupby(['Date','Neighborhood']).count()
    final_df = final_df.drop(columns=[ 'DBA Name','Location Start Date',
                           'Location End Date'])
    return final_df

df = open_neighborhoods()
neighborhoods = get_neighborhoods(df)
df = open_businesses()
df = generate_dates_for_each_business(df)

df.to_csv('businesses_0.2.csv', index = True)
