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

    # aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_50)
    # nx = 5
    # ny = 5
    # ids = "49 47 46 42 41 39 37 36 29 27 24 22 21 14 12 11 9 7 6 48 45 26 5".split()
    # fig = plt.figure()
    # for i in range(1, nx*ny+1-2):
    #     ax = fig.add_subplot(ny,nx, i)
    #     id = int(ids[i-1])
    #     img = aruco.drawMarker(aruco_dict, id, 700)
    #     plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
    #     ax.axis("off")
    # plt.show()  

    # img = aruco.drawMarker(aruco_dict, 17, 700)
    # plt.imshow(img, cmap = mpl.cm.gray, interpolation = "nearest")
    # plt.axis('off')

    frame = cv2.imread("../images/maze_aruco.jpg")
    # frame = cv2.resize(frame, (frame.shape[1]//4,frame.shape[0]//4))
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
    print(len(ids))
    for i in range(len(ids)):
        c = corners[i][0]
        plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))
    plt.legend()
    # plt.show()

if __name__ == '__main__':
    main()