'''
 - threshold for colour -> find mask
 - mask image to remove the object
 - do maze detection
 - draw perceived ball location
'''

import cv2 
from image_test import maze_compression

def locate_corners(frame, lower_bound, upper_bound):
    # frame_blur = cv2.blur(frame, (5,5))
    mask = cv2.inRange(frame, lower_bound, upper_bound)
    cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )   

    cnts.sort(key=lambda cnt: cv2.contourArea(cnt), reverse=True)
    corners = [ cv2.minEnclosingCircle(cnt) for cnt in cnts[:4] ]

    cv2.drawContours(frame, cnts[:4], -1, (0, 0, 255), 2)
    cv2.imshow("masked", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()   
    return corners

def locate_ball(frame, lower_bound, upper_bound):
    # frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
    # frame_blur = cv2.blur(frame, (15,15))
    mask = cv2.inRange(frame, lower_bound, upper_bound )
    cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )   

    if len(cnts):
        cnts.sort(key=lambda cnt: cv2.contourArea(cnt), reverse=True)
        ((x,y), r) = cv2.minEnclosingCircle(cnts[0])
        inverted_mask = 255-mask
        masked_frame = cv2.bitwise_and(frame, frame, mask=inverted_mask)
        white_masked_frame = masked_frame + cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        return (x,y)
    return (None, None)


if __name__ == '__main__':
    # #                     H    S    V
    # lower_color_bounds = (30, 90, 0)
    # upper_color_bounds = (90, 255, 255)
    #                     B    G   R
    lower_color_bounds = (0, 128, 0)
    upper_color_bounds = (100, 255, 100)
    
    filename = "./images/maze_ball_trim.png"
    # filename = "./images/pi_camera_capture.jpg"
    frame = cv2.imread(filename)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # frame = cv2.resize(frame, (frame.shape[1]//3, frame.shape[0]//3))

    grid_size = (8,8)

    # TODO: colour threshold for the walls
    # frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # frame_threshold = cv2.inRange(frame_HSV, (0, 0, 73), (360, 21, 255))

    locate_corners(frame, lower_color_bounds, upper_color_bounds)

    # # find ball
    (x,y) = locate_ball(frame, lower_color_bounds, upper_color_bounds)
    if x and y:
        # generate compressed maze
        maze, ref_img = maze_compression(frame_gray, grid_size, 0.53, preprocess={'block': 255, 'blur':15, 'resize':5, 'adaptive':True})
        maze = cv2.cvtColor(maze*255, cv2.COLOR_GRAY2BGR)

        # mark the location of the ball
        cx = int(x/frame.shape[1] * (grid_size[1]*2 + 1))
        cy = int(y/frame.shape[0] * (grid_size[0]*2 + 1))
        maze[cy,cx,:] = (0,255,0)

        #enlarge
        maze = cv2.resize(maze, (ref_img.shape[1], ref_img.shape[0]), interpolation=cv2.INTER_NEAREST)

        cv2.imshow("img", maze)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
