import numpy as np
import cv2 as cv
from scipy.spatial import ConvexHull

def getCorners(img):
    # find Harris corners
    dst = cv.cornerHarris(img,2,3,0.04)
    dst = cv.dilate(dst,None)
    _, dst = cv.threshold(dst,0.2*dst.max(),255,0)

    # mask the center - we don't need any of that
    # dst[30:-30,30:-30] = 0
    
    # find centroids
    dst = np.uint8(dst)
    _, _, _, centroids = cv.connectedComponentsWithStats(dst)

    # for c in centroids:
    #     x = int(c[0])
    #     y = int(c[1])
    #     cv.circle(img, (x,y), 4, (0,255,0), thickness=-1)
    
    hull = ConvexHull(centroids)
    vertices = np.int32(centroids[hull.vertices])
    
    # img = cv.polylines(img, [vertices], True, (0,255,0), thickness=3)

    epsilon = 0.1*cv.arcLength(vertices,True)
    approx = cv.approxPolyDP(vertices,epsilon,True)
    # cv.drawContours(img, [approx], 0, (255,0,0), 1)

    return approx

def test1():
    filename = '../images/corners.png'
    img = cv.imread(filename)
    img = cv.resize(img, (480,480), interpolation=cv.INTER_NEAREST)
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv.cornerHarris(gray,2,3,0.04)
    #result is dilated for marking the corners, not important
    dst = cv.dilate(dst,None)
    # Threshold for an optimal value, it may vary depending on the image.
    img[dst>0.25*dst.max()]=[0,0,255]
    cv.imshow('dst',img)
    if cv.waitKey(0) & 0xff == 27:
        cv.destroyAllWindows()

def test2():
    filename = '../images/corners.png'
    img = cv.imread(filename)
    img = cv.resize(img, (240,240), interpolation=cv.INTER_NEAREST)
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

    corners = getCorners(gray)
    cv.drawContours(img, [corners], 0, (255,0,0), 1)

    cv.imshow("", img)
    cv.waitKey(0)
    cv.destroyAllWindows()

test2()

# from __future__ import print_function
# import cv2 as cv
# import numpy as np
# import argparse
# import random as rng
# rng.seed(12345)
# def thresh_callback(val):
#     threshold = val
#     # Detect edges using Canny
#     canny_output = cv.Canny(src_gray, threshold, threshold * 2)
#     # Find contours
#     contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
#     # Find the convex hull object for each contour
#     hull_list = []
#     for i in range(len(contours)):
#         hull = cv.convexHull(contours[i])
#         hull_list.append(hull)
#     # Draw contours + hull results
#     drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
#     for i in range(len(contours)):
#         color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
#         cv.drawContours(drawing, contours, i, color)
#         cv.drawContours(drawing, hull_list, i, color)
#     # Show in a window
#     cv.imshow('Contours', drawing)
# # Load source image
# parser = argparse.ArgumentParser(description='Code for Convex Hull tutorial.')
# parser.add_argument('--input', help='Path to input image.', default='../images/corners.png')
# args = parser.parse_args()
# src = cv.imread(cv.samples.findFile(args.input))
# src = cv.resize(src, (480,480), interpolation=cv.INTER_NEAREST)
# if src is None:
#     print('Could not open or find the image:', args.input)
#     exit(0)
# # Convert image to gray and blur it
# src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
# src_gray = cv.blur(src_gray, (5,5))
# # Create Window
# source_window = 'Source'
# cv.namedWindow(source_window)
# cv.imshow(source_window, src)
# max_thresh = 255
# thresh = 100 # initial threshold
# cv.createTrackbar('Canny thresh:', source_window, thresh, max_thresh, thresh_callback)
# thresh_callback(thresh)
# cv.waitKey()