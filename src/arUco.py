import cv2
from cv2 import aruco
# import matplotlib.pyplot as plt
# import matplotlib as mpl


def find_markers(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    avg_points = []
    if ids is not None:
        for i in range(len(ids)):
            c = corners[i][0]
            avg_points.append((c[:, 0].mean(), c[:, 1].mean()))
    frame_markers = aruco.drawDetectedMarkers(img, corners, ids)
    return avg_points, frame_markers


def main():
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)

    fig = plt.figure()
    nx = 5
    ny = 10
    for i in range(1, nx*ny+1):
        ax = fig.add_subplot(ny,nx, i)
        img = aruco.drawMarker(aruco_dict,i-1, 700)
        plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
        ax.axis("off")

    img = aruco.drawMarker(aruco_dict, 17, 700)
    plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
    plt.axis('off')

    frame = cv2.imread("../images/aruco_test_1.jpg")
    plt.figure()
    plt.imshow(frame)
    plt.show()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    frame_markers = aruco.drawDetectedMarkers(frame, corners, ids)
    plt.figure()
    plt.imshow(frame)
    plt.show()

    plt.figure()
    plt.imshow(frame_markers)
    for i in range(len(ids)):
        c = corners[i][0]
        plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()