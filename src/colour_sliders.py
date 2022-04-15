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

def kernel(val):
    global k
    k = val if val%2==1 else val+1
    imgChange()


def imgChange():
    mask = cv2.inRange(img, tuple(colour_thresh[0]), tuple(colour_thresh[1]))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k,k))
    mask = cv2.erode(mask, kernel)
    cv2.imshow(windowName, mask)


img = cv2.imread('../images/green.jpg')  # input
img = cv2.resize(img, (400, 600))
img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

colour_thresh = [[0, 0, 0], [255, 255, 255]]
k=1

windowName = 'image'

imgChange()
cv2.createTrackbar('lower[0]', windowName, 0, 255, L0)
cv2.createTrackbar('lower[1]', windowName, 0, 255, L1)
cv2.createTrackbar('lower[2]', windowName, 0, 255, L2)
cv2.createTrackbar('upper[0]', windowName, 255, 255, U0)
cv2.createTrackbar('upper[1]', windowName, 255, 255, U1)
cv2.createTrackbar('upper[2]', windowName, 255, 255, U2)
cv2.createTrackbar('kernel', windowName, 0, 31, kernel)

cv2.waitKey(0)
cv2.destroyAllWindows()
