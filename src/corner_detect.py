import numpy as np
import cv2
from scipy.spatial import ConvexHull

def getCorners(img, img2, block_size=10, ksize=3, k=0.04):
    # find Harris corners
    dst = cv2.cornerHarris(img, block_size, ksize, k)
    dst = cv2.dilate(dst,None)
    _, dst = cv2.threshold(dst,0.2*dst.max(),255,0)

    # mask the center - we don't need any of that
    # dst[30:-30,30:-30] = 0
    
    # find centroids
    dst = np.uint8(dst)
    _, _, _, centroids = cv2.connectedComponentsWithStats(dst)

    for c in centroids:
        x = int(c[0])
        y = int(c[1])
        cv2.circle(img2, (x,y), 4, (0,255,0), thickness=-1)
    
    hull = ConvexHull(centroids)
    vertices = np.int32(centroids[hull.vertices])
    
    img = cv2.polylines(img2, [vertices], True, (0,255,0), thickness=3)

    epsilon = 0.1*cv2.arcLength(vertices,True)
    approx = cv2.approxPolyDP(vertices,epsilon,True)
    cv2.drawContours(img2, [approx], 0, (255,0,0), 1)

    return approx

def test1():
    filename = '../images/corners.png'
    img = cv2.imread(filename)
    img = cv2.resize(img, (480,480), interpolation=cv2.INTER_NEAREST)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray,2,3,0.04)
    #result is dilated for marking the corners, not important
    dst = cv2.dilate(dst,None)
    # Threshold for an optimal value, it may vary depending on the image.
    img[dst>0.25*dst.max()]=[0,0,255]
    cv2.imshow('dst',img)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()

def test2():
    filename = '../images/corners.png'
    img = cv2.imread(filename)
    img = cv2.resize(img, (240,240), interpolation=cv2.INTER_NEAREST)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    corners = getCorners(gray, img)
    cv2.drawContours(img, [corners], 0, (255,0,0), 1)

    cv2.imshow("", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# test2()

def block_change(val):
    global block_size
    block_size = val
    imgchange(block_size, ksize, k)

def ksize_change(val):
    global ksize
    ksize = val if val%2 else val+1
    imgchange(block_size, ksize, k)

def k_change(val):
    global k
    k = val/100
    imgchange(block_size, ksize, k)


def imgchange(b, ks, k):
    gray_copy = gray.copy()
    image_copy = img.copy()
    getCorners(gray_copy, image_copy, b, ks, k/100.0)
    cv2.imshow(windowName, image_copy)


img = cv2.imread('../images/corners.png')  # input
img = cv2.resize(img, (240,240), interpolation=cv2.INTER_NEAREST)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

windowName = 'image'

block_size = 2
ksize = 3
k = 4

imgchange(2, 3, 0.04)
cv2.createTrackbar('Blocksize', windowName, block_size, 100, block_change)
cv2.createTrackbar('ksize', windowName, ksize, 31, ksize_change)
cv2.createTrackbar('k', windowName, k, 1000, k_change)

cv2.waitKey(0)
cv2.destroyAllWindows()
