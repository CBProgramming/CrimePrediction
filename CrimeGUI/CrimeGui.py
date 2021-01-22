import tkinter as tk
from PIL import ImageTk, Image

NEIGHBOURHOOD_COORDS = {
    "Lincoln Park": (0.08,0.25),
    "Westwood Heights": (0.365,0.72),
    "Sherwood Forest": (0.35,0.69)
    }

MINIMUM_WIDTH = 1000
MINIMUM_HEIGHT = 600
CANVAS_HEIGHT = 618
CANVAS_WIDTH = 1152
UI_FRAME_HEIGHT = 0.1
UI_FRAME_WIDTH = 0.35
UI_X = 0.0
UI_Y = 0.0
STATS_FRAME_HEIGHT = 1 - UI_FRAME_HEIGHT
STATS_FRAME_WIDTH = UI_FRAME_WIDTH
STATS_X = 0.0
STATS_Y = UI_FRAME_HEIGHT
MAP_LABEL_HEIGHT = 1
MAP_LABEL_WIDTH = 1 - UI_FRAME_WIDTH
MAP_X = UI_FRAME_WIDTH
MAP_Y = 0.0
GPS_MARKER_TO_MAP_SCALE = 0.03

### INITIALIZE MAIN WINDOW ###
root = tk.Tk()
root.state('zoomed')
root.minsize(MINIMUM_WIDTH, MINIMUM_HEIGHT)

canvas = tk.Canvas(root, height = CANVAS_HEIGHT, width = CANVAS_WIDTH)
canvas.pack()

### INITIALIZE INNER FRAMES ###
ui_frame = tk.Frame(root, bg = 'blue')
ui_frame.place(relwidth = UI_FRAME_WIDTH, relheight = UI_FRAME_HEIGHT,
               relx = UI_X, rely = UI_Y)

stats_frame = tk.Frame(root, bg = 'red')
stats_frame.place(relwidth = STATS_FRAME_WIDTH,
                  relheight = STATS_FRAME_HEIGHT,
                  relx = STATS_X, rely = STATS_Y)

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
    map_image = Image.open("sf_map.png")
    gps_marker_image = Image.open("gps.png")
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
    map_label.bind('<Configure>',adjust_map_size)
    map_label.place(relwidth = MAP_LABEL_WIDTH,
                    relheight = MAP_LABEL_HEIGHT,
                relx = MAP_X, rely = MAP_Y)
    return sf_map_photo, map_label, map_image
    
### HOTSPOTS SHOULD BE HOTSPOTS CALCULATED BY THE MACHINE LEARNING MODEL ###
hotspots = ["Lincoln Park","Westwood Heights","Sherwood Forest"]
### create image with relevant gps hotspots, call this once hotspots are calculated
sf_map_photo, map_label, sf_map_image = place_gps_markers(hotspots)





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

root.mainloop()
