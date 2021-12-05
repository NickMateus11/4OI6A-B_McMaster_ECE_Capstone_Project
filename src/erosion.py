import cv2
from image_test import maze_compression

from image_utils import draw_grid


def kVal(val):
    global k
    k = val if val%2==1 else val+1
    imgchange(thresh, blur, sens, block, c, k)

def threshchange(val):
    global thresh
    thresh = val
    imgchange(thresh, blur, sens, block, c, k)

def blurchange(val):
    global blur
    blur = val if val>0 else 1
    imgchange(thresh, blur, sens, block, c, k)

def senschange(val):
    global sens
    sens = val/100.0
    imgchange(thresh, blur, sens, block, c, k)

def blockchange(val):
    global block
    block = val*2 + 1 if val>0 else 3
    imgchange(thresh, blur, sens, block, c, k)

def cchange(val):
    global c
    c = val/100.0
    imgchange(thresh, blur, sens, block, c, k)

def imgchange(thresh_val, blur_val, sens_val, block_val, c_val, k):
    imageCopy = show_img.copy()

    blr_img = cv2.blur(imageCopy, (blur_val,blur_val))
    
    if resize_required:
        blr_img = cv2.resize(blr_img, (img.shape[1]//5, img.shape[0]//5))

    bin_img = blr_img
    # (_, bin_img) = cv2.threshold(blr_img, thresh_val, 255, cv2.THRESH_BINARY)
    bin_img = cv2.adaptiveThreshold(blr_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_val, c_val)

    #erosion
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (k,k))
    morph_img = cv2.morphologyEx(bin_img, cv2.MORPH_ERODE, kernel)
    morph_img = cv2.bitwise_not(morph_img)

    draw_grid(morph_img, y_cell, x_cell)

    # TODO: use the preprocess features more
    (cmpr_img, ref_maze) = maze_compression(morph_img, (y_cell, x_cell), 4, sens_val) 

    cmpr_img = cv2.resize(
        cmpr_img*255, (ref_maze.shape[1], ref_maze.shape[0]), interpolation=cv2.INTER_NEAREST,)
    # bin_img = cv2.resize(bin_img, (ref_maze.shape[1], ref_maze.shape[0]), interpolation=cv2.INTER_NEAREST)

    final_frame = cv2.hconcat((cmpr_img, morph_img))
    cv2.imshow(windowName, final_frame)


# binary threshold
# blur
# sensitivity

resize_required = True
x_cell = 8
y_cell = 8

img = cv2.imread('./images/maze_ball0.png')  # input
# img = cv2.imread('./images/maze_real0.png')  # input
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
show_img = img
# if resize_required:
#     show_img = cv2.resize(img, (img.shape[1]//5, img.shape[0]//5))

# frame_HSV = cv2.cvtColor(show_img, cv2.COLOR_BGR2HSV)
# img = cv2.inRange(frame_HSV, (0, 0, 73), (360, 21, 255))

thresh = 150
blur = 15
sens = 0.83
block = 11
c = 2
k = 1

windowName = 'image'

cv2.imshow(windowName, show_img)
cv2.createTrackbar('Blur', windowName, 15, 100, blurchange)
cv2.createTrackbar('Threshold**broken', windowName, 150, 255, threshchange)
cv2.createTrackbar('Sens', windowName, 83, 100, senschange)
cv2.createTrackbar('Block', windowName, 11, 255, blockchange)
cv2.createTrackbar('C', windowName, 2, 255, cchange)
cv2.createTrackbar('K', windowName, 1, 100, kVal)

# or vconcat for vertical concatenation


cv2.waitKey(0)
cv2.destroyAllWindows()
