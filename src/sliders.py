import cv2
from image_test import maze_compression


def threshchange(val):
    global thresh
    thresh = val
    imgchange(thresh, blur, sens)


def blurchange(val):
    global blur
    if val == 0:
        blur = 1
    else:
        blur = val
    imgchange(thresh, blur, sens)


def senschange(val):
    global sens
    sens = val/100.0
    imgchange(thresh, blur, sens)


def imgchange(thresh_val, blur_val, sens_val):
    imageCopy = img.copy()
    blr_img = cv2.blur(imageCopy, (blur_val, blur_val))
    # rsz_img = cv2.resize(blr_img, (blr_img.shape[1]//5, blr_img.shape[0]//5))
    (_, bin_img) = cv2.threshold(blr_img, thresh_val, 255, cv2.THRESH_BINARY)
    (cmpr_img, ref_maze) = maze_compression(bin_img, (11, 11), 4, sens)
    cmpr_img = cv2.resize(
        cmpr_img*255, (ref_maze.shape[1], ref_maze.shape[0]), interpolation=cv2.INTER_NEAREST)
    bin_img = cv2.resize(
        bin_img, (ref_maze.shape[1], ref_maze.shape[0]), interpolation=cv2.INTER_NEAREST)
    final_frame = cv2.hconcat((cmpr_img, bin_img))
    cv2.imshow(windowName, final_frame)


# binary threshold
# blur
# sensitivity
img = cv2.imread('./images/maze0.jpg', cv2.IMREAD_GRAYSCALE)  # input
# resized_img = cv2.resize(img, (img.shape[1]//5, img.shape[0]//5))

thresh = 150
blur = 15
sens = 0.83

windowName = 'image'

cv2.imshow(windowName, img)
cv2.createTrackbar('Blur', windowName, 15, 30, blurchange)
cv2.createTrackbar('Threshold', windowName, 150, 255, threshchange)
cv2.createTrackbar('Sens', windowName, 83, 100, senschange)

# or vconcat for vertical concatenation


cv2.waitKey(0)
cv2.destroyAllWindows()
