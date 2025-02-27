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
    if (CALENDAR.winfo_ismapped()):
        CALENDAR.place_forget()
    x_data = data.loc[data[DATE_COL_KEY].str.contains(calendar_date)]
    if (x_data.empty):
        place_gps_markers([])
        hide_previous_results()
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
            place_gps_markers([])
            calculating_results()
            load_model(x_data, y_data, neighbourhoods_data, model_key, features_key)
        except:
            hide_previous_results()
            messagebox.showerror(FEATURES_NOT_IN_DATA_TITLE, FEATURES_NOT_IN_DATA_MESSAGE + COMMA_SPACE.join(features_selected))

def calculating_results():
    TITLE_LABEL.configure(fg = TEXT_COLOUR)
    TITLE_TEXT.set(TITLE_CALCULATING)
    for i in range(NUM_HOTSPOTS):
        NEIGHBOURHOOD_LABELS[i].configure(fg = BACKGROUND_COLOUR)
        HOTSPOT_VALUE_LABELS[i].configure(fg = BACKGROUND_COLOUR)
    ROOT.update()

def hide_previous_results():
    TITLE_LABEL.configure(fg = BACKGROUND_COLOUR)
    TITLE_TEXT.set(TITLE_CALCULATING)
    for i in range(NUM_HOTSPOTS):
        NEIGHBOURHOOD_LABELS[i].configure(fg = BACKGROUND_COLOUR)
        HOTSPOT_VALUE_LABELS[i].configure(fg = BACKGROUND_COLOUR)
    ROOT.update()

def load_model(x_data, y_data, neighbourhoods_data, model_key, features_key):
    model_tag = MODEL_FILE_TAGS[model_key]
    feature_tag = FEATURE_FILE_TAGS[features_key]
    file_path = MODEL_PATH + model_tag + MODEL_FEATURE_SEPARATOR + feature_tag
    try:
        with open(file_path, 'rb') as f:
            model = pickle.load(f)
            make_prediction(model, x_data, y_data, neighbourhoods_data)
    except:
        hide_previous_results()
        messagebox.showerror(MODEL_NOT_LOADED_TITLE, MODEL_NOT_LOADED_MESSAGE + file_path)

def make_prediction(model, x_data, y_data, neighbourhoods_data):
    y_predict = model.predict(x_data)
    y_data,y_predict,neighbourhoods_data = merge_sub_neighbourhoods(y_data,y_predict,neighbourhoods_data)
    neighbourhoods_data.reset_index(drop=True, inplace=True)
    actual_neighbourhoods_data = neighbourhoods_data.copy()
    x = 0
    predicted_hotspot_values = []
    predicted_hotspot_neighbourhoods = []
    actual_hotspot_values = []
    actual_hotspot_neighbourhoods = []
    while x < NUM_HOTSPOTS:
        predicted_index_max = np.argmax(y_predict)
        predicted_hotspot_values.append(y_predict[predicted_index_max])
        predicted_hotspot_neighbourhoods.append(neighbourhoods_data.at[predicted_index_max,NEIGHBOURHOOD_COL_KEY])
        y_predict = np.delete(y_predict,predicted_index_max)
        neighbourhoods_data = neighbourhoods_data.drop([predicted_index_max])
        neighbourhoods_data.reset_index(drop=True, inplace=True)
        actual_index_max = np.argmax(y_data)
        actual_hotspot_values.append(y_data[actual_index_max])
        actual_hotspot_neighbourhoods.append(actual_neighbourhoods_data.at[actual_index_max,NEIGHBOURHOOD_COL_KEY])
        y_data = np.delete(y_data,actual_index_max)
        actual_neighbourhoods_data = actual_neighbourhoods_data.drop([actual_index_max])
        actual_neighbourhoods_data.reset_index(drop=True, inplace=True)
        x += 1
    lowest_actual_hotspot_value = actual_hotspot_values[NUM_HOTSPOTS - 1]
    x = 0
    while x < len(y_data):
        if y_data[x] == lowest_actual_hotspot_value:
            actual_hotspot_neighbourhoods.append(actual_neighbourhoods_data.at[x,NEIGHBOURHOOD_COL_KEY])
        x += 1
    sf_map_photo, map_label = place_gps_markers(predicted_hotspot_neighbourhoods)
    update_text(predicted_hotspot_neighbourhoods,predicted_hotspot_values)
    colour = TITLE_LABEL["foreground"]
    display_label_text(predicted_hotspot_neighbourhoods, actual_hotspot_neighbourhoods)
       
def get_non_negative_value(value):
    if value < 0:
        return 0
    else:
        return value

def merge_sub_neighbourhoods(y_data,y_predict,neighbourhoods_data):
    y_data = pd.DataFrame(y_data).to_numpy().flatten()
    indexes_to_remove = []
    for parent_key in PARENT_NEIGHBOURHOODS:
        parent_index = neighbourhoods_data.index[neighbourhoods_data[NEIGHBOURHOOD_COL_KEY] == parent_key].tolist()[0]
        y_predict_parent_value = get_non_negative_value(y_predict[parent_index])
        y_data_parent_value = get_non_negative_value(y_data[parent_index])
        for sub_neighbourhood in PARENT_NEIGHBOURHOODS[parent_key]:
            sub_neighbourhood_index = neighbourhoods_data.index[neighbourhoods_data[NEIGHBOURHOOD_COL_KEY] == sub_neighbourhood].tolist()[0]
            indexes_to_remove.append(sub_neighbourhood_index)
            y_predict_sub_neighbourhood_value = get_non_negative_value(y_predict[sub_neighbourhood_index])
            y_predict_parent_value = y_predict_parent_value + y_predict_sub_neighbourhood_value
            y_data_sub_neighbourhood_value = get_non_negative_value(y_data[sub_neighbourhood_index])
            y_data_parent_value = y_data_parent_value + y_data_sub_neighbourhood_value
        y_predict[parent_index] = y_predict_parent_value
        y_data[parent_index] = y_data_parent_value
    neighbourhoods_data = neighbourhoods_data.drop(neighbourhoods_data.index[indexes_to_remove])
    indexes_to_remove.sort(reverse=True)
    for index in indexes_to_remove:
        y_predict = np.delete(y_predict,index)
        y_data = np.delete(y_data,index)
    return y_data,y_predict,neighbourhoods_data 

### UI FRAME ###
def setup_ui():
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
        CALENDAR.lift()

def date_selected():
    CALENDAR.place_forget()
    calendar_date = CALENDAR.selection_get().strftime("%d/%m/%Y")
    data_to_filter = DATA_FILE.copy()
    check_date_data = data_to_filter.loc[data_to_filter['Date'].str.contains(calendar_date)]

    if (check_date_data.empty):
        place_gps_markers([])
        hide_previous_results()
        DATE_BUTTON_TEXT.set(DATE_DROPDOWN_HELP_TEXT)
        messagebox.showerror(NO_DATA_FOUND_TITLE, NO_DATA_FOUND_MESSAGE)
    else:
        DATE_BUTTON_TEXT.set(calendar_date)
        MODEL_KEY = SELECTED_MODEL.get()
        FEATURES_KEY = SELECTED_FEATURES.get()
        if (MODEL_KEY != "" and FEATURES_KEY != "" and MODEL_KEY in MODELS and FEATURES_KEY in FEATURE_SELECTION):
            filter_data(data_to_filter, MODEL_KEY, FEATURES_KEY,calendar_date)

def update_text(neighbourhoods,values):
    for i in range(NUM_HOTSPOTS):
        NEIGHBOURHOOD_LABEL_STRINGS[i].set(neighbourhoods[i])
        if values:
            HOTSPOT_VALUE_LABEL_INTS[i].set(int(round(values[i],0)))
    reposition_neighborhood_labels()

def reposition_neighborhood_labels():
    if (TITLE_LABEL.winfo_ismapped()):
        TITLE_LABEL.place_forget()
    TITLE_LABEL.place(relx = TITLE_LABEL_REL_X, rely = TITLE_LABEL_REL_Y)
    title_height = TITLE_LABEL.winfo_height()
    title_y = TITLE_LABEL.winfo_rooty()
    label_rel_y = NEIGHBORHOOD_LABELS_REL_Y
    for i in range(NUM_HOTSPOTS):
        if (NEIGHBOURHOOD_LABELS[i].winfo_ismapped()):
            NEIGHBOURHOOD_LABELS[i].place_forget()
        NEIGHBOURHOOD_LABELS[i].place(relx = NEIGHBOURHOOD_LABELS_REL_X, rely = label_rel_y)
        if (HOTSPOT_VALUE_LABELS[i].winfo_ismapped()):
            HOTSPOT_VALUE_LABELS[i].place_forget()
        HOTSPOT_VALUE_LABELS[i].place(relx = PREDICTION_VALUE_REL_X, rely = label_rel_y)
        label_height = NEIGHBOURHOOD_LABELS[i].winfo_height()
        window_height = ROOT.winfo_height()
        label_rel_y = label_rel_y + (1/window_height*label_height)

def display_label_text(predicted_hotspot_neighbourhoods, actual_hotspot_neighbourhoods):
    TITLE_LABEL.configure(fg = TEXT_COLOUR)
    TITLE_TEXT.set(TITLE_PREDICTIONS)
    for i in range(NUM_HOTSPOTS):
        if predicted_hotspot_neighbourhoods[i] in actual_hotspot_neighbourhoods:
            NEIGHBOURHOOD_LABELS[i].configure(fg = CORRECT_COLOUR)
            HOTSPOT_VALUE_LABELS[i].configure(fg = CORRECT_COLOUR)
        else:
            NEIGHBOURHOOD_LABELS[i].configure(fg = INCORRECT_COLOUR)
            HOTSPOT_VALUE_LABELS[i].configure(fg = INCORRECT_COLOUR)

### MAP FRAME ###
def screen_resized(config_event):
    height = config_event.height
    adjust_map_size(height)
    reposition_neighborhood_labels()
            
def adjust_map_size(height):
    photo_height = sf_map_photo.height()
    suggested_width = int(height/(sf_map_photo.height())*(sf_map_photo.width()))
    if (map_label.winfo_width() >= suggested_width):
        width = suggested_width
    else:
        width = map_label.winfo_width()
        height = int(width/(sf_map_photo.width())*(sf_map_photo.height()))
    sf_map_copy = map_image.copy()
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
    global map_image
    global sf_map_photo
    global map_label
    map_image = Image.open(MAP_FILENAME)
    sf_map_photo = ImageTk.PhotoImage(map_image)
    map_label = tk.Label(ROOT, image = sf_map_photo)
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
    map_label.bind(CONFIGURE_EVENT_STRING,screen_resized)
    map_label.place(relwidth = MAP_LABEL_WIDTH,
                    relheight = MAP_LABEL_HEIGHT,
                relx = MAP_X, rely = MAP_Y)
    return sf_map_photo, map_label

### OPEN FILE ###
def open_file():
    try:
        DATA_FILE = pd.read_csv(DEFAULT_FILE_NAME+ CSV_FILE_EXTENSION)
    except:
        messagebox.showerror(FILE_NOT_FOUND_TITLE, FILE_NOT_FOUND_MESSAGE + DEFAULT_FILE_NAME + CSV_FILE_EXTENSION)
    return DATA_FILE

### INITIALISE VARIABLE LISTS ###
def initialise_neighbourhood_string_vars():
    string_vars = []
    for i in range(NUM_HOTSPOTS):
        string_vars.append(tk.StringVar())
    return string_vars

def initialise_neighbourhood_prediction_int_vars():
    int_vars = []
    for i in range(NUM_HOTSPOTS):
        int_vars.append(tk.IntVar())
    return int_vars

def initialise_neighbourhood_labels():
    labels = []
    for i in range(NUM_HOTSPOTS):
        labels.append(tk.Label(UI_FRAME, bg = BACKGROUND_COLOUR, textvariable = NEIGHBOURHOOD_LABEL_STRINGS[i], font = TEXT_DISPLAY_FONT, padx=1, fg = BACKGROUND_COLOUR))
    return labels

def initialise_hotspot_value_labels():
    labels = []
    for i in range(NUM_HOTSPOTS):
        labels.append(tk.Label(UI_FRAME, bg = BACKGROUND_COLOUR, textvariable = HOTSPOT_VALUE_LABEL_INTS[i], font = TEXT_DISPLAY_FONT, padx=1, fg = BACKGROUND_COLOUR))
    return labels


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
F_REGRESSION_NAME, CHI2_NAME, ADABOOST_NAME, EQUAL_DATA_NAME, ALL_BUS_NAME = "F-Regression","Chi-Squared","AdaBoost","Equal\n Selection","All\n Business"
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
ANN_NAME = "ANN\n (MLP)"
DECISION_TREE_NAME = "Decision\n Tree"
ELASTIC_NET_NAME = "Elastic\n Net"
LASSO_NAME = "Lasso"
LINERAR_REGRESSION_NAME = "Linear\n Regression"
RANDOM_FOREST_NAME = "Random\n Forest"
RIDGE_REGRESSION_NAME = "Ridge\n Regression"
SVM_NAME = "SVM"


MODELS = [ANN_NAME,
          DECISION_TREE_NAME,
          ELASTIC_NET_NAME,
          LASSO_NAME,
          LINERAR_REGRESSION_NAME,
          RANDOM_FOREST_NAME,
          RIDGE_REGRESSION_NAME,
          SVM_NAME]

MODEL_FILE_TAGS = {
    ANN_NAME: "multi_layer_perceptron",
    DECISION_TREE_NAME : "decision_tree",
    ELASTIC_NET_NAME : "elastic_net",
    LASSO_NAME : "lasso",
    LINERAR_REGRESSION_NAME: "linear_regression",
    RANDOM_FOREST_NAME: "random_forest",
    RIDGE_REGRESSION_NAME: "ridge_regression",
    SVM_NAME : "svm"
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
TITLE_LABEL_REL_X = 0.05
TITLE_LABEL_REL_Y = 0.15
LABEL_Y_GAP = 0.05
PREDICTION_VALUE_REL_X = TITLE_LABEL_REL_X
NEIGHBOURHOOD_LABELS_REL_X = 0.2
NEIGHBORHOOD_LABELS_REL_Y = TITLE_LABEL_REL_Y + LABEL_Y_GAP
MAP_LABEL_HEIGHT = 1
MAP_LABEL_WIDTH = 1 - UI_FRAME_WIDTH
MAP_X = UI_FRAME_WIDTH
MAP_Y = 0.0
GPS_MARKER_TO_MAP_SCALE = 0.03
NUM_HOTSPOTS = 15

### INITIALIZE MAIN WINDOW ###
ROOT = tk.Tk()
ROOT.state('zoomed')
ROOT.minsize(MINIMUM_WIDTH, MINIMUM_HEIGHT)
canvas = tk.Canvas(ROOT, height = CANVAS_HEIGHT, width = CANVAS_WIDTH)
canvas.pack()

### Define GUI components
TEXT_COLOUR = "white"
CORRECT_COLOUR = "green"
INCORRECT_COLOUR = "red"
BACKGROUND_COLOUR = "#000832"
TEXT_DISPLAY_FONT = "Arial 16"
DATE_BUTTON = tk.Button()
UI_FRAME = tk.Frame(ROOT, bg = BACKGROUND_COLOUR)
CALENDAR = Calendar(UI_FRAME, selectmode = "day")
SELECTED_MODEL = tk.StringVar()
SELECTED_FEATURES = tk.StringVar()
DATE_BUTTON_TEXT = tk.StringVar()
TITLE_TEXT = tk.StringVar()
TITLE_CALCULATING = "Calculating..."
TITLE_PREDICTIONS = "Hotspot Predictions"
MODEL_KEY = SELECTED_MODEL.get()
FEATURES_KEY = SELECTED_FEATURES.get()
TITLE_LABEL = tk.Label(UI_FRAME, bg = BACKGROUND_COLOUR, textvariable = TITLE_TEXT, font = TEXT_DISPLAY_FONT + " bold", padx=1, fg = BACKGROUND_COLOUR)
NEIGHBOURHOOD_LABEL_STRINGS = initialise_neighbourhood_string_vars()
NEIGHBOURHOOD_LABELS = initialise_neighbourhood_labels()
HOTSPOT_VALUE_LABEL_INTS = initialise_neighbourhood_prediction_int_vars()
HOTSPOT_VALUE_LABELS = initialise_hotspot_value_labels()

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
    "Alamo Square":(0.51,0.335),
    "Anza Vista":(0.45,0.29),
    "Balboa Terrace":(0.285,0.748),
    "Bayview":(0.775,0.72),
    "Bernal Heights":(0.615,0.665),
    "Buena Vista":(0.46,0.42),
    "Candlestick Point SRA":(0.79,0.932),
    "Central Waterfront":(0.80,0.508),
    "Civic Center":(0.59,0.295),
    "Clarendon Heights":(0.415,0.5),
    "Cole Valley":(0.395,0.445),
    "Corona Heights":(0.474,0.453),
    "Cow Hollow":(0.501,0.133),
    "Crocker Amazon":(0.47,0.935),
    "Diamond Heights":(0.445,0.642),
    "Downtown / Union Square":(0.635,0.23),
    "Duboce Triangle":(0.525,0.415),
    "Eureka Valley":(0.49,0.498),
    "Excelsior":(0.53,0.861),
    "Financial District":(0.72,0.165),
    "Forest Hill":(0.328,0.591),
    "Forest Knolls":(0.35,0.514),
    "Glen Park":(0.50,0.701),
    "Golden Gate Heights":(0.28,0.57),
    "Golden Gate Park":(0.172,0.394),
    "Haight Ashbury":(0.42,0.39),
    "Hayes Valley":(0.544,0.366),
    "Hunters Point":(0.89,0.808),
    "Ingleside":(0.365,0.855),
    "Ingleside Terraces":(0.29,0.814),
    "Inner Richmond":(0.318,0.287),
    "Inner Sunset":(0.29,0.46),
    "Lake Street":(0.248,0.239),
    "Lakeshore":(0.133,0.825),
    "Laurel Heights / Jordan Park":(0.39,0.259),
    "Lincoln Park / Ft. Miley":(0.084,0.25),
    "Little Hollywood":(0.71,0.96),
    "Lone Mountain":(0.391,0.31),
    "Lower Pacific Heights":(0.501,0.243),
    "Marina":(0.49,0.088),
    "Merced Heights":(0.289,0.859),
    "Merced Manor":(0.225,0.733),
    "Midtown Terrace":(0.385,0.585),
    "Miraloma Park":(0.404,0.677),
    "Mission":(0.626,0.493),
    "Mission Bay":(0.776,0.397),
    "Mission Dolores":(0.56,0.45),
    "Mission Terrace":(0.45,0.825),
    "Monterey Heights":(0.33,0.742),
    "Mt. Davidson Manor":(0.316,0.774),
    "Nob Hill":(0.625,0.177),
    "Noe Valley":(0.524,0.582),
    "North Beach":(0.648,0.081),
    "Northern Waterfront":(0.64,0.049),
    "Oceanview":(0.35,0.917),
    "Outer Mission":(0.42,0.92),
    "Outer Richmond":(0.092,0.317),
    "Outer Sunset":(0.074,0.501),
    "Pacific Heights":(0.5,0.177),
    "Panhandle":(0.452,0.337),
    "Parkside":(0.19,0.62),
    "Portola":(0.635,0.813),
    "Potrero Hill":(0.727,0.497),
    "Presidio Heights":(0.385,0.218),
    "Presidio National Park":(0.316,0.142),
    "Russian Hill":(0.608,0.108),
    "Seacliff":(0.162,0.23),
    "Sherwood Forest":(0.35,0.69),
    "Silver Terrace":(0.715,0.736),
    "South Beach":(0.774,0.292),
    "South of Market":(0.665,0.338),
    "St. Francis Wood":(0.294,0.71),
    "Stonestown":(0.21,0.84),
    "Sunnyside":(0.422,0.77),
    "Telegraph Hill":(0.685,0.116),
    "Tenderloin":(0.632,0.28),
    "Treasure Island":(0.93,0.04),
    "Upper Market":(0.436,0.557),
    "Visitacion Valley":(0.635,0.921),
    "West Portal":(0.294,0.655),
    "Western Addition":(0.528,0.286),
    "Westwood Highlands":(0.368,0.72),
    "Westwood Park":(0.364,0.793),
    "Yerba Buena Island":(0.717,0.253)
    }

# setup initial GUI display
place_gps_markers([])
setup_ui()
ROOT.mainloop()
