'''
 - threshold for colour -> find mask
 - mask image to remove the object
 - do maze detection
 - draw perceived ball location
'''

import cv2
import numpy as np
from image_test import maze_compression


def locate_corners(frame, lower_bound, upper_bound, convert_HSV=False, return_frame=False):
    if convert_HSV:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frame, lower_bound, upper_bound)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    # mask = cv2.erode(mask, kernel)
    if return_frame:
        return mask

    # old opencv version
    if cv2.__version__[0] == '3':
        cnts = cv2.findContours(mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)[1]
    else:
        cnts = cv2.findContours(mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)[0]

    cnts = sorted(cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)
    
    for c in cnts[:4]:
        area = cv2.contourArea(c) 
        # print(area)
        # if area < 10: # likely not what we are looking for
        #     break
    else:
        return [cv2.minEnclosingCircle(cnt) for cnt in cnts[:4]]

    # return [cv2.minEnclosingCircle(cnt) for cnt in cnts[:4]]
    
    # cv2.drawContours(frame, cnts[:4], -1, (0, 0, 255), 2)
    # cv2.imshow("masked", frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    # return np.array([])


def locate_ball(frame, lower_bound, upper_bound, convert_HSV=False):
    if convert_HSV:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(frame, lower_bound, upper_bound)

    # old opencv version
    if cv2.__version__[0] == '3':
        cnts = cv2.findContours(mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)[1]
    else:
        cnts = cv2.findContours(mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)[0]

    if len(cnts):
        cnts = sorted(cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)
        if cv2.minEnclosingCircle(cnts[0])[1] > 5: # check radius 
            ((x, y), r) = cv2.minEnclosingCircle(cnts[0])
            return (x, y), r, mask
        
    return (None, None), None, None


def locate_hazards(frame, lower_bound, upper_bound, convert_HSV=False):
    if convert_HSV:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(frame, lower_bound, upper_bound)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    mask = cv2.erode(mask, kernel)

    # old opencv version
    if cv2.__version__[0] == '3':
        cnts = cv2.findContours(mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)[1]
    else:
        cnts = cv2.findContours(mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)[0]

    cnts = sorted(cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)
    areas = [cv2.contourArea(cnt) for cnt in cnts[:len(cnts)]]
    count = 0
    for i in range(len(areas)):
        if areas[i] > 30:
            count += 1
        else: break

    hazards = [cv2.minEnclosingCircle(cnt) for cnt in cnts[:count]]

    # cv2.drawContours(frame, cnts[:count], -1, (0, 0, 255), 2)
    # cv2.imshow("masked", frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    hazard_coords = []
    for (x,y), _ in hazards:
        hazard_coords.append( (x,y) )
    
    return hazard_coords


if __name__ == '__main__':
    # #                     H    S    V
    lower_color_bounds = (40, 100, 45)
    upper_color_bounds = (90, 255, 255)
    #                     B    G   R
    # lower_color_bounds = (0, 100, 0)
    # upper_color_bounds = (100, 255, 100)

    filename = "../images/obstacle.jpg"
    # filename = "./images/pi_camera_capture.jpg"
    frame = cv2.imread(filename)
    # frame = cv2.resize(frame, (frame.shape[1]//3, frame.shape[0]//3))

    grid_size = (8, 8)

    # TODO: colour threshold for the walls
    # frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # frame_threshold = cv2.inRange(frame_HSV, (0, 0, 73), (360, 21, 255))

    locate_hazards(frame, lower_color_bounds,
                   upper_color_bounds, convert_HSV=True)
    # # find ball
    # import numpy as np
    # (x, y), r, mask = locate_ball(
    #     frame, lower_color_bounds, upper_color_bounds, convert_HSV=True)
    # locate_hazards(frame, lower_color_bounds,
    #                upper_color_bounds, convert_HSV=True)
    # # inv_mask = cv2.bitwise_not(mask)
    # # mask = np.stack((mask,)*3, axis=-1)
    # # frame = cv2.bitwise_or(frame, frame, mask=inv_mask)
    # # frame = frame + mask
    # # # frame = cv2.circle(frame, (int(x),int(y)), int(r*0.7), color=(255,)*3, thickness=-1)
    # # cv2.imshow("",mask)
    # # cv2.waitKey(0)
    # # cv2.imshow("",frame)
    # # cv2.waitKey(0)
    # # cv2.destroyAllWindows()

    # frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # if x and y:
    #     # generate compressed maze
    #     maze, ref_img = maze_compression(frame_gray, grid_size, 0.67, preprocess={
    #                                      'block': 75, 'c': 14, 'blur': 3, 'resize': 1, 'adaptive': True})
    #     maze = cv2.cvtColor(maze*255, cv2.COLOR_GRAY2BGR)

    #     # mark the location of the ball
    #     cx = int(x/frame.shape[1] * (grid_size[1]*2 + 1))
    #     cy = int(y/frame.shape[0] * (grid_size[0]*2 + 1))
    #     maze[cy, cx, :] = (255, 0, 0)

    #     # enlarge
    #     maze = cv2.resize(
    #         maze, (ref_img.shape[1], ref_img.shape[0]), interpolation=cv2.INTER_NEAREST)

    #     cv2.imshow("img", maze)

    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
