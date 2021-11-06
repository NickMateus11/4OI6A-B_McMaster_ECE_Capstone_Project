import cv2

from image_utils import draw_grid
from image_test import maze_compression

def click_and_mark(event, x, y, flags, param):

    if event in [cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN]:
        # unpack params
        image_copy, grids, end_rect, start_rect = param
        grid_y, grid_x = grids

        img_dim_y, img_dim_x = image_copy.shape[0], image_copy.shape[1]

        # calc grid cell
        x_cell =  x // (img_dim_x / grid_x) 
        y_cell =  y // (img_dim_y / grid_y)

        x_start = int(x_cell   * (img_dim_x / grid_x))
        y_start = int(y_cell   * (img_dim_y / grid_y))
        x_end   = int(x_start  + (img_dim_x / grid_x)) 
        y_end   = int(y_start  + (img_dim_y / grid_y))

        # copy and overwrite image
        image_copy[:] = image.copy()
        
        # place start cell
        if event == cv2.EVENT_LBUTTONDOWN:
            start_rect[:] = [(x_start, y_start) , (x_end, y_end)]
            cv2.rectangle(image_copy, (x_start, y_start) , (x_end, y_end), (0, 255, 0), 4)
            if end_rect and not end_rect == start_rect:
                cv2.rectangle(image_copy, end_rect[0], end_rect[1], (180, 100, 255), 4)
            else: 
                end_rect[:] = []
        # place end cell
        else:
            end_rect[:] = [(x_start, y_start) , (x_end, y_end)]
            cv2.rectangle(image_copy, end_rect[0], end_rect[1], (180, 100, 255), 4)
            if start_rect and not end_rect == start_rect:
                cv2.rectangle(image_copy, start_rect[0], start_rect[1], (0, 255, 0), 4)
            else: 
                start_rect[:] = []


start_rect = []
end_rect = []

grid_x = 11
grid_y = 11

# compress maze image
image, ref_img = maze_compression("./images/maze0.jpg", (grid_y, grid_x), 4, 0.83)
image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
image = cv2.resize(image, (ref_img.shape[1]*2,ref_img.shape[0]*2), interpolation=cv2.INTER_NEAREST)

img_dim_y, img_dim_x = image.shape[0], image.shape[1]

draw_grid(image, grid_y*2+1, grid_x*2+1)

win_name = "image"
cv2.imshow(win_name, image)

image_copy = image.copy()
cv2.setMouseCallback(win_name, click_and_mark, \
    param=[image_copy, (grid_y*2+1, grid_x*2+1), end_rect, start_rect])

while (True):
    cv2.imshow(win_name, image_copy)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    if not cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE):        
        break        

cv2.destroyAllWindows()