import numpy as np
import cv2, PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

# fig = plt.figure()
# nx = 5
# ny = 10
# # for i in range(1, nx*ny+1):
# #     ax = fig.add_subplot(ny,nx, i)
# #     img = aruco.drawMarker(aruco_dict,i-1, 700)
# #     plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
# #     ax.axis("off")

# img = aruco.drawMarker(aruco_dict, 17, 700)
# plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
# plt.axis('off')
# plt.show()

frame = cv2.imread("../images/maze_aruco.jpg")
plt.figure()
plt.imshow(frame)
plt.show()

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters =  aruco.DetectorParameters_create()
corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

plt.figure()
plt.imshow(frame_markers)
for i in range(len(ids)):
    c = corners[i][0]
    plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))
plt.legend()
plt.show()