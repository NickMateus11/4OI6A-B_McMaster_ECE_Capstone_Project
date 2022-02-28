import cv2
from image_test import maze_compression
from image_utils import draw_grid


def threshchange(val):
    global thresh
    thresh = val
    imgchange(thresh, blur, sens, block, c)

def blurchange(val):
    global blur
    blur = val if val>0 else 1
    imgchange(thresh, blur, sens, block, c)

def senschange(val):
    global sens
    sens = val/100.0
    imgchange(thresh, blur, sens, block, c)

def blockchange(val):
    global block
    block = val*2 + 1 if val>0 else 3
    imgchange(thresh, blur, sens, block, c)

def cchange(val):
    global c
    c = val/100.0
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
    (cmpr_img, ref_maze) = maze_compression(imageCopy, (y_cell, x_cell), 4, sens_val, 
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

    final_frame = cv2.hconcat((cmpr_img, ref_maze))
    upscaled = cv2.resize(final_frame, (x//2 * 2, y//2), interpolation=cv2.INTER_NEAREST)
    cv2.imshow(windowName, upscaled)


# binary threshold
# blur
# sensitivity

resize_required = True
x_cell = 8
y_cell = 8

img = cv2.imread('./images/test3.png')  # input
y,x,_ = img.shape
#resize if too big
scale = 0.25
y=int(y//scale)
x=int(x//scale)

# img = cv2.resize(img, (200, 100))

# img = cv2.imread('./images/maze_real0.png')  # input
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# frame_HSV = cv2.cvtColor(show_img, cv2.COLOR_BGR2HSV)
# img = cv2.inRange(frame_HSV, (0, 0, 73), (360, 21, 255))

thresh = 150
blur = 15
sens = 0.83
block = 11
c = 2

windowName = 'image'

imgchange(thresh, blur, sens, block, c)
cv2.createTrackbar('Blur', windowName, 15, 100, blurchange)
cv2.createTrackbar('Threshold**broken', windowName, 150, 255, threshchange)
cv2.createTrackbar('Sens', windowName, 83, 100, senschange)
cv2.createTrackbar('Block', windowName, 11, 255, blockchange)
cv2.createTrackbar('C', windowName, 2, 255, cchange)


cv2.waitKey(0)
cv2.destroyAllWindows()
