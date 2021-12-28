'''
 - threshold for colour -> find mask
 - mask image to remove the object
 - do maze detection
 - draw perceived ball location
'''

import cv2 
from image_test import maze_compression

def locate_ball(frame):
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
    frame_blur = cv2.blur(frame_hsv, (15,15))
    mask = cv2.inRange(frame_blur, lower_color_bounds, upper_color_bounds )
    cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )   

    for cnt in cnts:
        if cv2.contourArea(cnt)**0.5 > max(frame_hsv.shape)/20.0:
            ((x,y), r) = cv2.minEnclosingCircle(cnt)

            inverted_mask = 255-mask
            masked_frame = cv2.bitwise_and(frame, frame, mask=inverted_mask)
            white_masked_frame = masked_frame + cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            return white_masked_frame, (x,y)

#                     H    S    V
lower_color_bounds = (30, 90, 0)
upper_color_bounds = (90, 255, 255)
 
filename = "./images/maze_ball_trim.png"
frame = cv2.imread(filename)
frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# frame = cv2.resize(frame, (frame.shape[1]//3, frame.shape[0]//3))

grid_size = (8,8)

# TODO: colour threshold for the walls
# frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# frame_threshold = cv2.inRange(frame_HSV, (0, 0, 73), (360, 21, 255))

# find ball
frame, (x,y) = locate_ball(frame)

# generate compressed maze
maze, ref_img = maze_compression(frame_gray, grid_size, 4, 0.53, preprocess={'block': 255, 'blur':15, 'resize':5, 'adaptive':True})
# maze = cv2.cvtColor(maze*255, cv2.COLOR_GRAY2BGR)

# mark the location of the ball
cx = int(x/frame.shape[1] * (grid_size[1]*2 + 1))
cy = int(y/frame.shape[0] * (grid_size[0]*2 + 1))
# maze[cy][cx] = (0,255,0)

#enlarge
maze = cv2.resize(maze*255, (ref_img.shape[1], ref_img.shape[0]), interpolation=cv2.INTER_NEAREST)

cv2.imshow("img", maze)

cv2.waitKey(0)
cv2.destroyAllWindows()
