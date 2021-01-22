import tkinter as tk
import pandas as pd
from PIL import ImageTk, Image
from tkinter import messagebox
from tkcalendar import *
from datetime import date

### Define file variables ###
DEFAULT_FILE_NAME = "data"
CSV_FILE_EXTENSION = ".csv"
MAP_FILENAME = "sf_map.png"
GPS_FILENAME = "gps.png"
DATA_FILE = pd.DataFrame()
FILE_NOT_FOUND_TITLE = "File not found"
FILE_NOT_FOUND_MESSAGE = ("No file found for the selected features.\n\n" + 
"Ensure there is a file in the root folder with the following name: ")

### Define event strings
CONFIGURE_EVENT_STRING = '<Configure>'
CALENDAR_SELECTED_EVENT_STRING = '<<CalendarSelected>>'

### Define helper text ###
MODEL_DROPDOWN_HELP_TEXT = "Select\nModel"
DATE_DROPDOWN_HELP_TEXT = "Select\nDate"
FEATURES_DROPDOWN_HELP_TEXT = "Select\nFeature Set"

### Define Neighbourhood Coordinates ###
NEIGHBOURHOOD_COORDS = {
    "Lincoln Park": (0.08,0.25),
    "Westwood Heights": (0.365,0.72),
    "Sherwood Forest": (0.35,0.69)
    }

### Define feature selection variables ###
F_REGRESSION_NAME, CHI2_NAME = "F-Regression","Chi-Squared"
FEATURES = [F_REGRESSION_NAME, CHI2_NAME]
FEATURE_FILE_TAGS = {
    F_REGRESSION_NAME : "_f_regression",
    CHI2_NAME : "_chi2"
    }

### Define model variables ###
SVM_NAME, RANDOM_FOREST_NAME, DECISION_TREE_NAME = "SVM","Random Forest","Decision Tree"
MODELS = [SVM_NAME, RANDOM_FOREST_NAME, DECISION_TREE_NAME]


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

### UI FRAME ###
def model_selected(window):
    model_key = selected_model.get()
    if (model_key in MODELS):
        print("oof")# and calendar_date !=

def features_selected(window):
    features_key = selected_features.get()
    if (features_key in FEATURES):
        file_tag = FEATURE_FILE_TAGS[features_key]
        try:
            print(features_key)
            print(FEATURE_FILE_TAGS[features_key])
            DATA_FILE = pd.read_csv(DEFAULT_FILE_NAME + file_tag + CSV_FILE_EXTENSION)
            print(DATA_FILE.head())
        except:
            messagebox.showerror(FILE_NOT_FOUND_TITLE, FILE_NOT_FOUND_MESSAGE + DEFAULT_FILE_NAME + file_tag + CSV_FILE_EXTENSION)

        
def show_calendar():
    if (calendar.winfo_ismapped()):
        calendar.place_forget()
    else:
        calendar.place(relx = CALENDAR_REL_X, rely = CALENDAR_REL_Y)

def date_selected(date_button):
    calendar_date = calendar.selection_get()
    date_button.config(text = calendar_date)
    calendar.place_forget()

def setup_dropdown_menus():
    ui_frame.place(relwidth = UI_FRAME_WIDTH, relheight = UI_FRAME_HEIGHT,
                   relx = UI_X, rely = UI_Y)
    date_button = tk.Button(ui_frame, text = DATE_DROPDOWN_HELP_TEXT, command = show_calendar)
    calendar.bind(CALENDAR_SELECTED_EVENT_STRING, lambda x = None: date_selected(date_button))
    
    date_button.place(relwidth = DROPDOWN_WIDTH, relheight = DROPDOWN_HEIGHT,
                    relx = DROPDOWN_REL_XS[0], rely = DROPDOWN_REL_Y)
    selected_model.set(MODEL_DROPDOWN_HELP_TEXT)
    model_dropdown = tk.OptionMenu(ui_frame, selected_model, *MODELS, command = model_selected)
    model_dropdown.place(relwidth = DROPDOWN_WIDTH, relheight = DROPDOWN_HEIGHT,
                    relx = DROPDOWN_REL_XS[1], rely = DROPDOWN_REL_Y)
    selected_features.set(FEATURES_DROPDOWN_HELP_TEXT)
    features_dropdown = tk.OptionMenu(ui_frame, selected_features, *FEATURES, command = features_selected)
    features_dropdown.place(relwidth = DROPDOWN_WIDTH, relheight = DROPDOWN_HEIGHT,
                    relx = DROPDOWN_REL_XS[2], rely = DROPDOWN_REL_Y)


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
    map_label = tk.Label(root, image = sf_map_photo)
    map_label.bind(CONFIGURE_EVENT_STRING,adjust_map_size)
    map_label.place(relwidth = MAP_LABEL_WIDTH,
                    relheight = MAP_LABEL_HEIGHT,
                relx = MAP_X, rely = MAP_Y)
    return sf_map_photo, map_label, map_image


### INITIALIZE MAIN WINDOW ###
root = tk.Tk()
root.state('zoomed')
root.minsize(MINIMUM_WIDTH, MINIMUM_HEIGHT)
canvas = tk.Canvas(root, height = CANVAS_HEIGHT, width = CANVAS_WIDTH)
canvas.pack()


### HOTSPOTS SHOULD BE HOTSPOTS CALCULATED BY THE MACHINE LEARNING MODEL ###
hotspots = ["Lincoln Park","Westwood Heights","Sherwood Forest"]



### create image with relevant gps hotspots, call this once hotspots are calculated
sf_map_photo, map_label, sf_map_image = place_gps_markers(hotspots)
### setup dropdowns ###
ui_frame = tk.Frame(root, bg = 'blue')
today = date.today()
calendar = Calendar(ui_frame, selectmode = "day", year = 2021, month = 1, day = 1, maxdate=today)
calendar_date = calendar.selection_get()
selected_model = tk.StringVar()
selected_features = tk.StringVar()
model_key = selected_model.get()
setup_dropdown_menus()




root.mainloop()

#create fram to place things on
#frame = tk.Frame(root, bg = '#99b3ff')
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

