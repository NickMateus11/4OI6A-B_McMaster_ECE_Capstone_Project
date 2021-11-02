import cv2
from trim_maze import trim
import numpy as np


def click_and_mark(event, x, y, flags, param):
    global image_copy, green_rect, pink_rect

    if event == cv2.EVENT_LBUTTONDOWN:
        # find the grid square that the mouse is in, colour it
        x_cell =  x // (img_dim_x / grid_x) 
        y_cell =  y // (img_dim_y / grid_y)

        x_start = int(x_cell   * (img_dim_x / grid_x))
        y_start = int(y_cell   * (img_dim_y / grid_y))
        x_end   = int(x_start  + (img_dim_x / grid_x)) 
        y_end   = int(y_start  + (img_dim_y / grid_y))

        # reset image, then draw new rect
        image_copy = image.copy()
        green_rect = [(x_start, y_start) , (x_end, y_end)]
        cv2.rectangle(image_copy, (x_start, y_start) , (x_end, y_end), (0, 255, 0), 4)
        if pink_rect and not pink_rect == green_rect:
            cv2.rectangle(image_copy, pink_rect[0], pink_rect[1], (180, 100, 255), 4)
        else: 
            pink_rect = []
    
    if event == cv2.EVENT_RBUTTONDOWN:
        # find the grid square that the mouse is in, colour it
        x_cell =  x // (img_dim_x / grid_x) 
        y_cell =  y // (img_dim_y / grid_y)

        x_start = int(x_cell   * (img_dim_x / grid_x))
        y_start = int(y_cell   * (img_dim_y / grid_y))
        x_end   = int(x_start  + (img_dim_x / grid_x)) 
        y_end   = int(y_start  + (img_dim_y / grid_y))

        # reset image, then draw new rect
        image_copy = image.copy()
        pink_rect = [(x_start, y_start) , (x_end, y_end)]
        cv2.rectangle(image_copy, pink_rect[0], pink_rect[1], (180, 100, 255), 4)
        if green_rect and not pink_rect == green_rect:
            cv2.rectangle(image_copy, green_rect[0], green_rect[1], (0, 255, 0), 4)
        else: 
            green_rect = []


def draw_grid(img, rows, cols):
    h, w, _ = img.shape

    # draw vertical lines
    for x in np.linspace(start=0, stop=w, num=cols+1):
        x = int(round(x))
        cv2.line(img, (x, 0), (x, h), color=(0,0,0), thickness=1)

    # draw horizontal lines
    for y in np.linspace(start=0, stop=h, num=rows+1):
        y = int(round(y))
        cv2.line(img, (0, y), (w, y), color=(0,0,0), thickness=1)


green_rect = []
pink_rect = []

grid_x = 11
grid_y = 11

# load, binary threshold, trim image
image = cv2.imread("./images/maze0.jpg")
(thresh, image) = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
image = trim(image)
img_dim_y, img_dim_x, _ = image.shape
draw_grid(image, grid_y, grid_x)

win_name = "image"
cv2.imshow(win_name, image)

cv2.setMouseCallback(win_name, click_and_mark)

image_copy = image.copy()
while (True):
    cv2.imshow(win_name, image_copy)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    if not cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE):        
        break        

cv2.destroyAllWindows()