import pandas as pd

def open_sfpd():
    df = pd.read_csv('SFPD_preprocessed.csv')
    return df

def open_businesses():
    df = pd.read_csv('businesses_0.3.csv')
    return df

def open_business_openings():
    df = pd.read_csv('businesses_openings.csv')
    return df

def open_business_closures():
    df = pd.read_csv('businesses_closures.csv')
    return df

def finalise_data(sfpd_data,businesses,openings,closures):
    sfpd_data.rename(columns={"1 day ago": "Crime 1 day ago",
                              "2 days ago": "Crime 2 days ago",
                              "3 days ago": "Crime 3 days ago",
                              "4 days ago": "Crime 4 days ago",
                              "5 days ago": "Crime 5 days ago",
                              "6 days ago": "Crime 6 days ago",
                              "7 days ago": "Crime 7 days ago",
                              "14 days ago": "Crime 14 days ago",
                              "30 days ago": "Crime 30 days ago",
                              "365 days ago": "Crime 365 days ago",
                              "Last 7 days": "Last 7 days crime",
                              "Last 14 days": "Last 14 days crime",
                              "Last 28 days": "Last 28 days crime"})
    sfpd_data['Number of businesses'] = businesses['Number of businesses']
    sfpd_data['Businesses 1 day ago'] = businesses['Businesses 1 day ago']
    sfpd_data['Businesses 2 days ago'] = businesses['Businesses 2 days ago']
    sfpd_data['Businesses 3 days ago'] = businesses['Businesses 3 days ago']
    sfpd_data['Businesses 4 days ago'] = businesses['Businesses 4 days ago']
    sfpd_data['Businesses 5 days ago'] = businesses['Businesses 5 days ago']
    sfpd_data['Businesses 6 days ago'] = businesses['Businesses 6 days ago']
    sfpd_data['Businesses 7 days ago'] = businesses['Businesses 7 days ago']
    sfpd_data['Businesses 14 days ago'] = businesses['Businesses 14 days ago']
    sfpd_data['Businesses 30 days ago'] = businesses['Businesses 30 days ago']
    sfpd_data['Businesses 365 days ago'] = businesses['Businesses 365 days ago']
    sfpd_data['Number of closures'] = closures['Closures']
    sfpd_data['Closures 1 day ago'] = closures['Closures 1 day ago']
    sfpd_data['Closures 2 days ago'] = closures['Closures 2 days ago']
    sfpd_data['Closures 3 days ago'] = closures['Closures 3 days ago']
    sfpd_data['Closures 4 days ago'] = closures['Closures 4 days ago']
    sfpd_data['Closures 5 days ago'] = closures['Closures 5 days ago']
    sfpd_data['Closures 6 days ago'] = closures['Closures 6 days ago']
    sfpd_data['Closures 7 days ago'] = closures['Closures 7 days ago']
    sfpd_data['Closures 14 days ago'] = closures['Closures 14 days ago']
    sfpd_data['Closures 30 days ago'] = closures['Closures 30 days ago']
    sfpd_data['Closures 365 days ago'] = closures['Closures 365 days ago']
    sfpd_data['Last 7 days closures'] = closures['Last 7 days closures']
    sfpd_data['Last 14 days closures'] = closures['Last 14 days closures']
    sfpd_data['Last 28 days closures'] = closures['Last 28 days closures']
    sfpd_data['Number of openings'] = openings['Openings']
    sfpd_data['Openings 1 day ago'] = openings['Openings 1 day ago']
    sfpd_data['Openings 2 days ago'] = openings['Openings 2 days ago']
    sfpd_data['Openings 3 days ago'] = openings['Openings 3 days ago']
    sfpd_data['Openings 4 days ago'] = openings['Openings 4 days ago']
    sfpd_data['Openings 5 days ago'] = openings['Openings 5 days ago']
    sfpd_data['Openings 6 days ago'] = openings['Openings 6 days ago']
    sfpd_data['Openings 7 days ago'] = openings['Openings 7 days ago']
    sfpd_data['Openings 14 days ago'] = openings['Openings 14 days ago']
    sfpd_data['Openings 30 days ago'] = openings['Openings 30 days ago']
    sfpd_data['Openings 365 days ago'] = openings['Openings 365 days ago']
    sfpd_data['Last 7 days openings'] = openings['Last 7 days openings']
    sfpd_data['Last 14 days openings'] = openings['Last 14 days openings']
    sfpd_data['Last 28 days openings'] = openings['Last 28 days openings']
    return sfpd_data
    

sfpd_data = open_sfpd()
businesses = open_businesses()
openings = open_business_openings()
closures = open_business_closures()
final_data = finalise_data(sfpd_data,businesses,openings,closures)
final_data.to_csv('finalised_data.csv', index = False)
