import cv2
from image_test import maze_compression
from image_utils import draw_grid


def threshchange(val):
    global thresh
    thresh = val
    imgchange(thresh, blur, sens, block, c)

def blurchange(val):
    global blur
    blur = val if val%2 else val+1
    imgchange(thresh, blur, sens, block, c)

def senschange(val):
    global sens
    sens = val/100
    imgchange(thresh, blur, sens, block, c)

def blockchange(val):
    global block
    block = val if val%2 else val+1 if val>1 else 3
    imgchange(thresh, blur, sens, block, c)

def cchange(val):
    global c
    c = val
    imgchange(thresh, blur, sens, block, c)

def imgchange(thresh_val, blur_val, sens_val, block_val, c_val):
    imageCopy = img.copy()

    # blr_img = cv2.blur(imageCopy, (blur_val,blur_val))

    # if resize_required:
    #     blr_img = cv2.resize(
    #         blr_img, (blr_img.shape[1]//5, blr_img.shape[0]//5))

    # (_, bin_img) = cv2.threshold(blr_img, thresh_val, 255, cv2.THRESH_BINARY)
    # bin_img = cv2.adaptiveThreshold(blr_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_val, c_val)

    # TODO: use the preprocess features more
    (cmpr_img, ref_maze) = maze_compression(imageCopy, (y_cell, x_cell), sens_val, 
                        trim=False,
                        preprocess={
                            'thresh':thresh_val, 
                            "blur":blur_val, 
                            "resize":1, 
                            "block":block_val,
                            "c":c_val, 
                            "adaptive": True
                        }) 

    cmpr_img = cv2.resize(cmpr_img*255, (ref_maze.shape[1], ref_maze.shape[0]), interpolation=cv2.INTER_NEAREST)
    # bin_img = cv2.resize(bin_img, (ref_maze.shape[1], ref_maze.shape[0]), interpolation=cv2.INTER_NEAREST)

    draw_grid(ref_maze, y_cell, x_cell, 1)
    cell_size_x = ref_maze.shape[1]/8
    cell_size_y = ref_maze.shape[0]/8
    c_x = int(cell_size_x//2)
    c_y = int(cell_size_y//2)

    col_left = int(3 * cell_size_x)
    row_top  = int(7 * cell_size_y)
    col_right = int(col_left+cell_size_x)
    row_bottom = int(row_top+cell_size_y)
    check_offset_width = int(max(min(cell_size_x, cell_size_y) / 4, 1))
    check_offset_depth = int(max(min(cell_size_x, cell_size_y) / 3, 1))

    ref_maze = cv2.cvtColor(ref_maze, cv2.COLOR_GRAY2BGR)
    cmpr_img = cv2.cvtColor(cmpr_img, cv2.COLOR_GRAY2BGR)

# top
    cv2.rectangle(ref_maze, 
                (col_left+c_x-check_offset_width//2, row_top), 
                (col_right-c_x+check_offset_width//2, row_top+check_offset_depth), (0,0,255), 1)
# bottom
    cv2.rectangle(ref_maze, 
                (col_left+c_x-check_offset_width//2, row_bottom-check_offset_depth),
                (col_right-c_x+check_offset_width//2, row_bottom), (0,0,255), 1)
# left
    cv2.rectangle(ref_maze, 
                (col_left, row_top+c_y-check_offset_width//2), 
                (col_left+check_offset_depth, row_bottom-c_y+check_offset_width//2), (0,0,255), 1)
# right
    cv2.rectangle(ref_maze, 
                (col_right-check_offset_depth, row_bottom-c_y-check_offset_width//2), 
                (col_right, row_bottom-c_y+check_offset_width//2), (0,0,255), 1)

    final_frame = cv2.hconcat((cmpr_img, ref_maze))
    upscaled = cv2.resize(final_frame, (x//2 * 2, y//2), interpolation=cv2.INTER_NEAREST)
    cv2.imshow(windowName, upscaled)


# binary threshold
# blur
# sensitivity

x_cell = 8
y_cell = 8

img = cv2.imread('./images/pi_camera_capture.jpg')  # input
y,x,_ = img.shape
#resize if too big
scale = 0.25
# scale = 1
y=int(y//scale)
x=int(x//scale)

# img = cv2.resize(img, (200, 100))

# img = cv2.imread('./images/maze_real0.png')  # input
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# frame_HSV = cv2.cvtColor(show_img, cv2.COLOR_BGR2HSV)
# img = cv2.inRange(frame_HSV, (0, 0, 73), (360, 21, 255))

thresh = 150
blur = 3
sens = 0.80
block = 43
c = 14

windowName = 'image'

imgchange(thresh, blur, sens, block, c)
cv2.createTrackbar('Blur', windowName, blur, 100, blurchange)
cv2.createTrackbar('Threshold', windowName, thresh, 255, threshchange)
cv2.createTrackbar('Sens', windowName, int(sens*100), 100, senschange)
cv2.createTrackbar('Block', windowName, block, 1023, blockchange)
cv2.createTrackbar('C', windowName, c, 100, cchange)


cv2.waitKey(0)
cv2.destroyAllWindows()
