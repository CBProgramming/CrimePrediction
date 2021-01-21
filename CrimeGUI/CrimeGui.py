import tkinter as tk
from PIL import ImageTk, Image

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


root = tk.Tk()
root.state('zoomed')

#create base canvas to define size of screen
canvas = tk.Canvas(root, height = CANVAS_HEIGHT, width = CANVAS_WIDTH)
canvas.pack()

ui_frame = tk.Frame(root, bg = 'blue')
ui_frame.place(relwidth = UI_FRAME_WIDTH, relheight = UI_FRAME_HEIGHT,
               relx = UI_X, rely = UI_Y)

stats_frame = tk.Frame(root, bg = 'red')
stats_frame.place(relwidth = STATS_FRAME_WIDTH,
                  relheight = STATS_FRAME_HEIGHT,
                  relx = STATS_X, rely = STATS_Y)

#for images

def adjust_image_size(label):
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
    
sf_map_image = Image.open("sf_map.png")
sf_map_photo = ImageTk.PhotoImage(sf_map_image)
map_label = tk.Label(root, image = sf_map_photo)
map_label.bind('<Configure>',adjust_image_size)
map_label.place(relwidth = MAP_LABEL_WIDTH,
                relheight = MAP_LABEL_HEIGHT,
                relx = MAP_X, rely = MAP_Y)

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
