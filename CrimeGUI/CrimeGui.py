import tkinter as tk
import pandas as pd
from PIL import ImageTk, Image
from tkinter import messagebox
from tkcalendar import *
from datetime import date
import pickle
import numpy as np

### FILER DATASET AND PREDICT ###
      
def filter_data(data, model_key, features_key,calendar_date):
    x_data = data.loc[data[DATE_COL_KEY].str.contains(calendar_date)]
    if (x_data.empty):
        DATE_BUTTON_TEXT.set(DATE_DROPDOWN_HELP_TEXT)
        messagebox.showerror(NO_DATA_FOUND_TITLE, NO_DATA_FOUND_MESSAGE)
    else:
        try:
            neighbourhoods_data = pd.DataFrame(x_data[NEIGHBOURHOOD_COL_KEY])
            neighbourhoods_data.reset_index(drop=True, inplace=True)
            y_data = pd.DataFrame(x_data[INCIDENT_COL_KEY])
            y_data.reset_index(drop=True, inplace=True)
            features_selected = FEATURES[features_key]
            x_data = x_data[features_selected]
            load_model(x_data, y_data, neighbourhoods_data, model_key, features_key)
        except:
            messagebox.showerror(FEATURES_NOT_IN_DATA_TITLE, FEATURES_NOT_IN_DATA_MESSAGE + COMMA_SPACE.join(features_selected))
        

def load_model(x_data, y_data, neighbourhoods_data, model_key, features_key):
    print("reached load model")
    model_tag = MODEL_FILE_TAGS[model_key]
    feature_tag = FEATURE_FILE_TAGS[features_key]
    file_path = MODEL_PATH + model_tag + MODEL_FEATURE_SEPARATOR + feature_tag
    print(file_path)
    try:
        with open(file_path, 'rb') as f:
            model = pickle.load(f)
            make_prediction(model, x_data, y_data, neighbourhoods_data)
    except:
        messagebox.showerror(MODEL_NOT_LOADED_TITLE, MODEL_NOT_LOADED_MESSAGE + file_path)

def make_prediction(model, x_data, y_data, neighbourhoods_data):
    print(x_data)
    print(y_data)
    print(neighbourhoods_data)
    print("Making prediction")
    y_predict = model.predict(x_data)
    print(y_predict)
    y_predict,neighbourhoods_data = merge_sub_neighbourhoods(y_predict,neighbourhoods_data)
    print(y_predict)
    x = 0
    #hotspot_indexes = []
    hotspot_values = []
    hotspot_neighbourhoods = []
    print(NUM_HOTSPOTS)
    while x < NUM_HOTSPOTS:
        index_max = np.argmax(y_predict)
        #print("\nIndex max = ",index_max)
        #hotspot_indexes.append(index_max)
        hotspot_values.append(y_predict[index_max])
        #print("Hotspot value = ",y_predict[index_max])
        #print("Hotspot values = ",hotspot_values)
        hotspot_neighbourhoods.append(neighbourhoods_data.at[index_max,NEIGHBOURHOOD_COL_KEY])
        #print("Hotspot neighbourhood = ",neighbourhoods_data.at[index_max,NEIGHBOURHOOD_COL_KEY])
        #print("Hotspot neighbourhoods = ",hotspot_neighbourhoods)
        y_predict = np.delete(y_predict,index_max)
        #print("Size of y = ",len(y_predict))
        neighbourhoods_data = neighbourhoods_data.drop([index_max])
        neighbourhoods_data.reset_index(drop=True, inplace=True)
        #print("Size of neighbourhoods",len(neighbourhoods_data.index))
        #print("Neighbourhoods:\n")
        #print(neighbourhoods_data)
        x += 1
    #print(hotspot_indexes)
    print(hotspot_values)
    print(hotspot_neighbourhoods)
    sf_map_photo, map_label, sf_map_image = place_gps_markers(hotspot_neighbourhoods)

def merge_sub_neighbourhoods(y_predict,neighbourhoods_data):
    indexes_to_remove = []
    for parent_key in PARENT_NEIGHBOURHOODS:
        parent_index = neighbourhoods_data.index[neighbourhoods_data[NEIGHBOURHOOD_COL_KEY] == parent_key].tolist()[0]
        parent_value = y_predict[parent_index]
        if parent_value < 0:
            parent_value = 0
        for sub_neighbourhood in PARENT_NEIGHBOURHOODS[parent_key]:
            sub_neighbourhood_index = neighbourhoods_data.index[neighbourhoods_data[NEIGHBOURHOOD_COL_KEY] == sub_neighbourhood].tolist()[0]
            indexes_to_remove.append(sub_neighbourhood_index)
            sub_neighbourhood_value = y_predict[sub_neighbourhood_index]
            if sub_neighbourhood_value < 0:
                sub_neighbourhood_value = 0
            parent_value = parent_value + sub_neighbourhood_value
        y_predict[parent_index] = parent_value
    neighbourhoods_data = neighbourhoods_data.drop(neighbourhoods_data.index[indexes_to_remove])
    indexes_to_remove.sort(reverse=True)
    for index in indexes_to_remove:
        y_predict = np.delete(y_predict,index)
    return y_predict,neighbourhoods_data
    
    

### UI FRAME ###
def setup_dropdown_menus():
    UI_FRAME.place(relwidth = UI_FRAME_WIDTH, relheight = UI_FRAME_HEIGHT,
                   relx = UI_X, rely = UI_Y)
    DATE_BUTTON_TEXT.set(DATE_DROPDOWN_HELP_TEXT)
    DATE_BUTTON = tk.Button(UI_FRAME, textvariable = DATE_BUTTON_TEXT, command = show_calendar)
    CALENDAR.bind(CALENDAR_SELECTED_EVENT_STRING, lambda x = None: date_selected())
    DATE_BUTTON.place(relwidth = DROPDOWN_WIDTH, relheight = DROPDOWN_HEIGHT,
                    relx = DROPDOWN_REL_XS[0], rely = DROPDOWN_REL_Y)
    SELECTED_MODEL.set(MODEL_DROPDOWN_HELP_TEXT)
    model_dropdown = tk.OptionMenu(UI_FRAME, SELECTED_MODEL, *MODELS, command = model_selected)
    model_dropdown.place(relwidth = DROPDOWN_WIDTH, relheight = DROPDOWN_HEIGHT,
                    relx = DROPDOWN_REL_XS[1], rely = DROPDOWN_REL_Y)
    SELECTED_FEATURES.set(FEATURES_DROPDOWN_HELP_TEXT)
    features_dropdown = tk.OptionMenu(UI_FRAME, SELECTED_FEATURES, *FEATURE_SELECTION, command = features_selected)
    features_dropdown.place(relwidth = DROPDOWN_WIDTH, relheight = DROPDOWN_HEIGHT,
                    relx = DROPDOWN_REL_XS[2], rely = DROPDOWN_REL_Y)
    
def model_selected(window):
    data_to_filter = DATA_FILE.copy()
    MODEL_KEY = SELECTED_MODEL.get()
    FEATURES_KEY = SELECTED_FEATURES.get()
    date_text = DATE_BUTTON_TEXT.get()
    if (MODEL_KEY not in MODELS):
        messagebox.showerror(NO_MODEL_FOUND_TITLE, NO_MODEL_FOUND_MESSAGE)
    elif (FEATURES_KEY != "" and FEATURES_KEY in FEATURE_SELECTION and date_text != DATE_DROPDOWN_HELP_TEXT):
            filter_data(data_to_filter, MODEL_KEY, FEATURES_KEY, date_text)

def features_selected(window):
    data_to_filter = DATA_FILE.copy()
    FEATURES_KEY = SELECTED_FEATURES.get()
    MODEL_KEY = SELECTED_MODEL.get()
    date_text = DATE_BUTTON_TEXT.get()
    if (FEATURES_KEY not in FEATURE_SELECTION):
        messagebox.showerror(NO_FEATURES_FOUND_TITLE, NO_FEATURES_FOUND_MESSAGE)
    elif (MODEL_KEY != "" and MODEL_KEY in MODELS and date_text != DATE_DROPDOWN_HELP_TEXT):
        filter_data(data_to_filter, MODEL_KEY, FEATURES_KEY, date_text)
 
def show_calendar():
    if (CALENDAR.winfo_ismapped()):
        CALENDAR.place_forget()
    else:
        CALENDAR.place(relx = CALENDAR_REL_X, rely = CALENDAR_REL_Y)

def date_selected():
    CALENDAR.place_forget()
    calendar_date = CALENDAR.selection_get().strftime("%Y-%m-%d")
    data_to_filter = DATA_FILE.copy()
    check_date_data = data_to_filter.loc[data_to_filter['Date'].str.contains(calendar_date)]
    if (check_date_data.empty):
        DATE_BUTTON_TEXT.set(DATE_DROPDOWN_HELP_TEXT)
        messagebox.showerror(NO_DATA_FOUND_TITLE, NO_DATA_FOUND_MESSAGE)
    else:
        DATE_BUTTON_TEXT.set(calendar_date)
        MODEL_KEY = SELECTED_MODEL.get()
        FEATURES_KEY = SELECTED_FEATURES.get()
        if (MODEL_KEY != "" and FEATURES_KEY != "" and MODEL_KEY in MODELS and FEATURES_KEY in FEATURE_SELECTION):
            filter_data(data_to_filter, MODEL_KEY, FEATURES_KEY,calendar_date)


### MAP FRAME ###
def adjust_map_size(label):
    photo_height = sf_map_photo.height()
    height = label.height
    suggested_width = int(height/(sf_map_photo.height())*(sf_map_photo.width()))
    if (map_label.winfo_width() >= suggested_width):
        width = suggested_width
    else:
        width = map_label.winfo_width()
        height = int(width/(sf_map_photo.width())*(sf_map_photo.height()))
    sf_map_copy = sf_map_image.copy()
    resized_map = sf_map_copy.resize((width, height))
    resized_photo = ImageTk.PhotoImage(resized_map)
    map_label.config(image = resized_photo)
    map_label.image = resized_photo

def adjust_gps_marker_size(marker,map_image):
    map_height = map_image.height
    map_width = map_image.width
    marker_height = int(map_height * GPS_MARKER_TO_MAP_SCALE)
    marker_width = int(marker.width/marker.height*marker_height)
    resized_marker = marker.resize((marker_width,marker_height))
    return resized_marker

def place_gps_markers(hotspots):
    map_image = Image.open(MAP_FILENAME)
    gps_marker_image = Image.open(GPS_FILENAME)
    gps_marker_image = adjust_gps_marker_size(gps_marker_image, map_image)
    map_height = map_image.height
    map_width = map_image.width
    for hotspot in hotspots:
        coords = NEIGHBOURHOOD_COORDS.get(hotspot)
        x = int(map_width * coords[0])
        y = int(map_height * coords[1])
        map_image.paste(gps_marker_image, (x, y), gps_marker_image)
    sf_map_photo = ImageTk.PhotoImage(map_image)
    #new_file_name = "hotspots.png" ### DELETE ME ###
    #sf_map_photo._PhotoImage__photo.write(new_file_name)  ### DELETE ME ###
    print(ROOT)
    components = canvas.slaves()
    print(components)
    map_label = tk.Label(ROOT, image = sf_map_photo)
    map_label.bind(CONFIGURE_EVENT_STRING,adjust_map_size)
    #adjust_map_size(sf_map_photo)
    map_label.place(relwidth = MAP_LABEL_WIDTH,
                    relheight = MAP_LABEL_HEIGHT,
                relx = MAP_X, rely = MAP_Y)
    print("made it")
    return sf_map_photo, map_label, map_image

### OPEN FILE ###
def open_file():
    try:
        DATA_FILE = pd.read_csv(DEFAULT_FILE_NAME+ CSV_FILE_EXTENSION)
    except:
        messagebox.showerror(FILE_NOT_FOUND_TITLE, FILE_NOT_FOUND_MESSAGE + DEFAULT_FILE_NAME + CSV_FILE_EXTENSION)
    return DATA_FILE


### Define file variables ###
DEFAULT_FILE_NAME = "data"
CSV_FILE_EXTENSION = ".csv"
MAP_FILENAME = "sf_map.png"
GPS_FILENAME = "gps.png"
DATA_FILE = pd.DataFrame()
FILTERED_DATA = pd.DataFrame()
DATA_FILE = open_file()
MODEL_FEATURE_SEPARATOR = "_"
MODEL_PATH = "Models/"
COMMA_SPACE = ", "
INCIDENT_COL_KEY = "Todays Reports"
NEIGHBOURHOOD_COL_KEY = "Neighborhood"
DATE_COL_KEY = "Date"

### Define Error Messages
FILE_NOT_FOUND_TITLE = "File not found"
FILE_NOT_FOUND_MESSAGE = ("Crime incident data file not found.\n\n" + 
"Ensure there is a file in the root folder with the following name: ")
NO_DATA_FOUND_TITLE = "No data found"
NO_DATA_FOUND_MESSAGE = ("No data for the selected date found.\n\n" + 
"Ensure there is a file in the root folder containing crime data for the selected date.")
NO_FEATURES_FOUND_TITLE = "Feature set not found"
NO_FEATURES_FOUND_MESSAGE = ("Feature set / model still in development.\n\n" + 
"Please select a different feature set.")
FEATURES_NOT_IN_DATA_TITLE = "Features not found"
FEATURES_NOT_IN_DATA_MESSAGE = ("The dataset does not contain features conforming to the " +
                                "feature selection moethod chosen.\n\n" +
                                "Ensure the dataset contains features for the following:\n")
NO_MODEL_FOUND_TITLE = "Model not found"
NO_MODEL_FOUND_MESSAGE = ("Feature set / model still in development.\n\n" + 
"Please select a different model and try again.")
MODEL_NOT_LOADED_TITLE = "Loading model failed"
MODEL_NOT_LOADED_MESSAGE = ("A machine learning model cannot be found for the specified " +
                            "model and feature selection.\n\n" +
                            "Ensure a pickled machine learning model exists to the following " +
                            "directory specification: ")

### Define event strings
CONFIGURE_EVENT_STRING = '<Configure>'
CALENDAR_SELECTED_EVENT_STRING = '<<CalendarSelected>>'

### Define GUI helper text ###
MODEL_DROPDOWN_HELP_TEXT = "Select\nModel"
DATE_DROPDOWN_HELP_TEXT = "Select\nDate"
FEATURES_DROPDOWN_HELP_TEXT = "Select\nFeature Set"

### Define feature selection variables ###
F_REGRESSION_NAME, CHI2_NAME, ADABOOST_NAME, EQUAL_DATA_NAME, ALL_BUS_NAME = "F-Regression","Chi-Squared","AdaBoost","Equal Selection","All Business"
FEATURE_SELECTION = [F_REGRESSION_NAME, CHI2_NAME, ADABOOST_NAME, EQUAL_DATA_NAME, ALL_BUS_NAME]
FEATURES = {
    F_REGRESSION_NAME : ['Reports 1 day ago', 'Reports 2 days ago', 'Reports 3 days ago',
                       'Reports 4 days ago', 'Reports 5 days ago', 'Reports 6 days ago',
                      'Reports 7 days ago','Reports 14 days ago','Reports 30 days ago','Reports 365 days ago'],
    CHI2_NAME : ['South of Market', 'Mission', 'Tenderloin', 'Number of businesses', 
               'Downtown / Union Square', 'Civic Center', 'Reports 365 days ago',
               'Reports 1 day ago','Reports 2 days ago','Reports 14 days ago'],
    ADABOOST_NAME : ['Reports 365 days ago', 'Reports 1 day ago', 'Reports 14 days ago', 'Reports 3 days ago', 
               'Reports 2 days ago', 'Reports 7 days ago', 'Number of businesses',
               'Reports 4 days ago','Reports 5 days ago','Closures 365 days ago'],
    EQUAL_DATA_NAME : ['Number of businesses', 'Last 28 days closures', 'Last 7 days openings',
                          'Last 14 days closures', 'Last 7 days closures','Reports 1 day ago',
                      'Reports 2 days ago', 'Reports 4 days ago', 'Reports 30 days ago', 'Reports 7 days ago'],
    ALL_BUS_NAME : ['Number of businesses', 'Last 28 days closures', 'Last 7 days openings',
                          'Last 14 days closures', 'Last 7 days closures','Number of openings',
                   'Openings 4 days ago','Openings 1 day ago', 'Openings 7 days ago', 'Openings 2 days ago']
    }
FEATURE_FILE_TAGS = {
    F_REGRESSION_NAME : "f_regression",
    CHI2_NAME : "chi2",
    ADABOOST_NAME : "adaboost",
    EQUAL_DATA_NAME : "equal_crime_and_business",
    ALL_BUS_NAME : "all_business"
    }

### Define model variables ###
SVM_NAME, RANDOM_FOREST_NAME, DECISION_TREE_NAME = "SVM","Random Forest","Decision Tree"
MODELS = [SVM_NAME, RANDOM_FOREST_NAME, DECISION_TREE_NAME]
MODEL_FILE_TAGS = {
    SVM_NAME : "svm",
    RANDOM_FOREST_NAME : "random_forest",
    DECISION_TREE_NAME : "decision_tree"
    }

### Define GUI geometry ###
MINIMUM_WIDTH = 1000
MINIMUM_HEIGHT = 600
CANVAS_HEIGHT = 618
CANVAS_WIDTH = 1152
UI_FRAME_HEIGHT = 1
UI_FRAME_WIDTH = 0.35
UI_X = 0.0
UI_Y = 0.0
DROPDOWN_HEIGHT = 0.1
DROPDOWN_WIDTH = 0.28
DROPDOWN_REL_X = 0.04
DROPDOWN_REL_Y = 0.03
DROPDOWN_REL_XS = [((DROPDOWN_REL_X*1) + (DROPDOWN_WIDTH*0)),
                   ((DROPDOWN_REL_X*2) + (DROPDOWN_WIDTH*1)),
                   ((DROPDOWN_REL_X*3) + (DROPDOWN_WIDTH*2))]
CALENDAR_REL_X = ((DROPDOWN_REL_X*1) + (DROPDOWN_WIDTH*0))
CALENDAR_REL_Y = (DROPDOWN_REL_Y + DROPDOWN_HEIGHT)
STATS_FRAME_HEIGHT = 1 - UI_FRAME_HEIGHT
STATS_FRAME_WIDTH = UI_FRAME_WIDTH
STATS_X = 0.0
STATS_Y = UI_FRAME_HEIGHT
MAP_LABEL_HEIGHT = 1
MAP_LABEL_WIDTH = 1 - UI_FRAME_WIDTH
MAP_X = UI_FRAME_WIDTH
MAP_Y = 0.0
GPS_MARKER_TO_MAP_SCALE = 0.03
NUM_HOTSPOTS = 10

### INITIALIZE MAIN WINDOW ###
ROOT = tk.Tk()
ROOT.state('zoomed')
ROOT.minsize(MINIMUM_WIDTH, MINIMUM_HEIGHT)
canvas = tk.Canvas(ROOT, height = CANVAS_HEIGHT, width = CANVAS_WIDTH)
canvas.pack()

### Define GUI components
DATE_BUTTON = tk.Button()
UI_FRAME = tk.Frame(ROOT, bg = 'blue')
CALENDAR = Calendar(UI_FRAME, selectmode = "day")
SELECTED_MODEL = tk.StringVar()
SELECTED_FEATURES = tk.StringVar()
DATE_BUTTON_TEXT = tk.StringVar()
MODEL_KEY = SELECTED_MODEL.get()
FEATURES_KEY = SELECTED_FEATURES.get()

### Define Neighbourhood Coordinates ###
PARENT_NEIGHBOURHOODS = {
    "Central Waterfront" : ["Dogpatch"],
    "Eureka Valley" : ["Dolores Heights","Castro"],
    "Buena Vista" : ["Ashbury Heights"],
    "Cole Valley" : ["Parnassus Heights"],
    "Bayview" : ["Apparel City", "Produce Market"],
    "Russian Hill" : ["Aquatic Park / Ft. Mason"],
    "North Beach" : ["Bret Harte"],
    "Western Addition" : ["Cathedral Hill", "Japantown"],
    "Downtown / Union Square" : ["Fairmount", "Chinatown", "Lower Nob Hill", "Polk Gulch"],
    "Mission Terrace" : ["Cayuga"],
    "Northern Waterfront" : ["Fishermans Wharf"],
    "Bernal Heights" : ["Holly Park", "Peralta Heights", "St. Marys Park"],
    "Hunters Point" : ["India Basin"],
    "Forest Hill" : ["Laguna Honda"],
    "Hayes Valley" : ["Lower Haight"],
    "Portola" : ["McLaren Park", "University Mound"],
    "South of Market" : ["Mint Hill"],
    "Stonestown" : ["Parkmerced"],
    "Presidio Heights" : ["Presidio Terrace"],
    "South Beach" : ["Rincon Hill"],
    "Potrero Hill" : ["Showplace Square"],
    "Visitacion Valley" : ["Sunnydale"],
    "Lincoln Park / Ft. Miley" : ["Sutro Heights"],
    "Cow Hollow" : ["Union Street"]
    }

NEIGHBOURHOOD_COORDS = {
    "Alamo Square":(0.51,0.34),
    "Anza Vista":(0.46,0.29),
    "Balboa Terrace":(0.29,0.75),
    "Bayview":(0.79,0.72),
    "Bernal Heights":(0.62,0.67),
    "Buena Vista":(0.46,0.43),
    "Candlestick Point SRA":(0.8,0.93),
    "Central Waterfront":(0.81,0.51),
    "Civic Center":(0.6,0.3),
    "Clarendon Heights":(0.42,0.5),
    "Cole Valley":(0.4,0.45),
    "Corona Heights":(0.48,0.46),
    "Cow Hollow":(0.51,0.13),
    "Crocker Amazon":(0.47,0.94),
    "Diamond Heights":(0.45,0.65),
    "Downtown / Union Square":(0.64,0.23),
    "Duboce Triangle":(0.53,0.42),
    "Eureka Valley":(0.5,0.5),
    "Excelsior":(0.54,0.87),
    "Financial District":(0.73,0.17),
    "Forest Hill":(0.33,0.6),
    "Forest Knolls":(0.36,0.52),
    "Glen Park":(0.51,0.7),
    "Golden Gate Heights":(0.29,0.57),
    "Golden Gate Park":(0.18,0.4),
    "Haight Ashbury":(0.42,0.39),
    "Hayes Valley":(0.55,0.37),
    "Hunters Point":(0.9,0.81),
    "Ingleside":(0.37,0.86),
    "Ingleside Terraces":(0.3,0.82),
    "Inner Richmond":(0.33,0.29),
    "Inner Sunset":(0.29,0.46),
    "Lake Street":(0.25,0.24),
    "Lakeshore":(0.14,0.83),
    "Laurel Heights / Jordan Park":(0.38,0.26),
    "Lincoln Park / Ft. Miley":(0.09,0.24),
    "Little Hollywood":(0.71,0.95),
    "Lone Mountain":(0.4,0.31),
    "Lower Pacific Heights":(0.51,0.25),
    "Marina":(0.5,0.09),
    "Merced Heights":(0.29,0.86),
    "Merced Manor":(0.23,0.74),
    "Midtown Terrace":(0.39,0.58),
    "Miraloma Park":(0.41,0.68),
    "Mission":(0.63,0.5),
    "Mission Bay":(0.78,0.4),
    "Mission Dolores":(0.57,0.45),
    "Mission Terrace":(0.46,0.83),
    "Monterey Heights":(0.33,0.74),
    "Mt. Davidson Manor":(0.32,0.78),
    "Nob Hill":(0.63,0.18),
    "Noe Valley":(0.53,0.59),
    "North Beach":(0.66,0.09),
    "Northern Waterfront":(0.64,0.05),
    "Oceanview":(0.36,0.92),
    "Outer Mission":(0.42,0.92),
    "Outer Richmond":(0.1,0.32),
    "Outer Sunset":(0.08,0.5),
    "Pacific Heights":(0.51,0.18),
    "Panhandle":(0.46,0.34),
    "Parkside":(0.2,0.62),
    "Portola":(0.64,0.82),
    "Potrero Hill":(0.73,0.5),
    "Presidio Heights":(0.39,0.22),
    "Presidio National Park":(0.33,0.14),
    "Russian Hill":(0.61,0.11),
    "Seacliff":(0.17,0.23),
    "Sherwood Forest":(0.36,0.69),
    "Silver Terrace":(0.72,0.74),
    "South Beach":(0.78,0.3),
    "South of Market":(0.67,0.34),
    "St. Francis Wood":(0.3,0.71),
    "Stonestown":(0.21,0.84),
    "Sunnyside":(0.43,0.77),
    "Telegraph Hill":(0.69,0.12),
    "Tenderloin":(0.64,0.28),
    "Treasure Island":(0.94,0.03),
    "Upper Market":(0.44,0.55),
    "Visitacion Valley":(0.64,0.92),
    "West Portal":(0.3,0.66),
    "Western Addition":(0.53,0.29),
    "Westwood Highlands":(0.37,0.72),
    "Westwood Park":(0.37,0.8),
    "Yerba Buena Island":(0.72,0.26)
    }

### HOTSPOTS SHOULD BE HOTSPOTS CALCULATED BY THE MACHINE LEARNING MODEL ###
hotspots = ["West Portal"]


### create image with relevant gps hotspots, call this once hotspots are calculated
sf_map_photo, map_label, sf_map_image = place_gps_markers(hotspots)
setup_dropdown_menus()

hotspots = ["Tenderloin"]
sf_map_photo, map_label, sf_map_image = place_gps_markers(hotspots)


ROOT.mainloop()

#create fram to place things on
#frame = tk.Frame(ROOT, bg = '#99b3ff')
#set width and height to that of parent
#frame.place(relwidth = 1, relheight = 1)
#set width and height to 0.8 of parent, and center
#frame.place(relwidth = 0.8, relheight = 0.8, relx = 0.1, rely = 0.1)

#def button_function(entry):
#    print(entry)

#create button in frame
#button = tk.Button(frame, text = "Test button", bg= 'blue', fg = 'red',
#                   command = lambda: button_function(entry.get()))
#button.pack(side = 'left')

#label = tk.Label(frame, text="Label")
#label.pack(side = 'left')

#entry = tk.Entry(frame, bg = 'green')
#entry.pack()

