import cv2
from image_test import maze_compression
from image_utils import draw_grid


def L0(val):
    colour_thresh[0][0] = val
    imgChange()
def L1(val):
    colour_thresh[0][1] = val
    imgChange()
def L2(val):
    colour_thresh[0][2] = val
    imgChange()
def U0(val):
    colour_thresh[1][0] = val
    imgChange()
def U1(val):
    colour_thresh[1][1] = val
    imgChange()
def U2(val):
    colour_thresh[1][2] = val
    imgChange()

def imgChange():
    mask = cv2.inRange(img, tuple(colour_thresh[0]), tuple(colour_thresh[1]))
    cv2.imshow(windowName, mask)


img = cv2.imread('../images/pi_camera_capture_8.jpg')  # input

# img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# img = cv2.inRange(frame_HSV, (0, 0, 73), (360, 21, 255))

colour_thresh = [[0,0,0], [255,255,255]]

windowName = 'image'

imgChange()
cv2.createTrackbar('lower[0]', windowName, 0, 255, L0)
cv2.createTrackbar('lower[1]', windowName, 0, 255, L1)
cv2.createTrackbar('lower[2]', windowName, 0, 255, L2)
cv2.createTrackbar('upper[0]', windowName, 255, 255, U0)
cv2.createTrackbar('upper[1]', windowName, 255, 255, U1)
cv2.createTrackbar('upper[2]', windowName, 255, 255, U2)

cv2.waitKey(0)
cv2.destroyAllWindows()
