# # import the necessary packages
import numpy as np
import argparse
import cv2
# from skimage.filters import threshold_local
import imutils

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

def skew1(args):
	# load the image and grab the source coordinates (i.e. the list of
	# of (x, y) points)
	# NOTE: using the 'eval' function is bad form, but for this example
	# let's just roll with it -- in future posts I'll show you how to
	# automatically determine the coordinates without pre-supplying them
	image = cv2.imread(args["image"])
	pts = np.array(eval(args["coords"]), dtype = "float32")
	# apply the four point tranform to obtain a "birds eye view" of
	# the image
	warped = four_point_transform(image, pts)
	# show the original and warped images
	cv2.imshow("Original", image)
	cv2.imshow("Warped", warped)
	cv2.waitKey(0)

	return warped

##########################################
# auto perspective change - using contours
def skew2(args):
	# # construct the argument parser and parse the arguments
	# ap = argparse.ArgumentParser()
	# ap.add_argument("-i", "--image", required = True,
	# 	help = "Path to the image to be scanned")
	# args = vars(ap.parse_args())

	# load the image and compute the ratio of the old height
	# to the new height, clone it, and resize it
	image = cv2.imread(args["image"])
	ratio = image.shape[0] / 500.0
	orig = image.copy()
	image = imutils.resize(image, height = 500)
	# convert the image to grayscale, blur it, and find edges
	# in the image
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (31, 31), 0)
	bin_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41, 6)
	bin_img = cv2.GaussianBlur(bin_img, (3, 3), 0)
	edged = cv2.Canny(bin_img, 75, 200)
	# show the original image and the edge detected image
	print("STEP 1: Edge Detection")
	cv2.imshow("Image", bin_img)
	cv2.imshow("Edged", edged)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	# find the contours in the edged image, keeping only the
	# largest ones, and initialize the screen contour
	cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break
	# show the contour (outline) of the piece of paper
	print("STEP 2: Find contours of paper")
	# cv2.drawContours(image, cnts, -1, (0, 0, 255), 2)
	cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
	cv2.imshow("Outline", image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	# apply the four point transform to obtain a top-down
	# view of the original image
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

	# convert the warped image to grayscale, then threshold it
	# to give it that 'black and white' paper effect
	warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	# T = threshold_local(warped, 11, offset = 10, method = "gaussian")
	# warped = (warped > T).astype("uint8") * 255

	# show the original and scanned images
	print("STEP 3: Apply perspective transform")
	cv2.imshow("Original", imutils.resize(orig, height = 650))
	cv2.imshow("Scanned", imutils.resize(warped, height = 650))
	cv2.waitKey(0)

	return warped


if __name__ == '__main__':  
    # construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", help = "path to the image file")
	ap.add_argument("-c", "--coords", help = "comma seperated list of source points", required=False)
	ap.add_argument("-f", "--find-corners", required=False, action="store_true")
	args = vars(ap.parse_args())
	
	if args["coords"]:
		res = skew1(args)
		print(cv2.imwrite("res.png", res))
	elif args["find_corners"]:
		import colour_thresholding as cthresh
		frame = cv2.imread(args["image"])
		corners = cthresh.locate_corners(frame, (0, 100, 0), (100, 255, 100))
		args["coords"] = str([(c[0][0],c[0][1]) for c in corners])
		print(args)
		res = skew1(args)
		print(cv2.imwrite("res.png", res))
	else:
		res = skew2(args)
		print(cv2.imwrite("res.png", res))

# Execution Example:
# python .\skew_correction.py -i ..\images\transform.jpg --coords "[(108, 195), (420, 160), (511, 341), (203, 466)]"
# python .\skew_correction.py -i ..\images\pi_camera_capture.jpg --cords "[(84,40),(237,41),(245,202),(73,200)]"





