import cv2
import numpy as np
from time import time

from image_test import maze_compression
from image_utils import draw_grid

if __name__ == '__main__':
    x_grids = 8
    y_grids = 8
    wall_size = 4  # hard coded

    sensitivity = 0.53

    start_time = time()
    iters = 100
    
    img_name = "./images/maze_ball_trim.png"
    img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)  # input

    for _ in range(iters):
        new_maze, reference_maze = maze_compression(img, (y_grids, x_grids), wall_size, sensitivity, 
                            preprocess={'block': 255, 'blur':15, 'resize':5, 'adaptive':True})

    maze_compressed = cv2.resize(
        new_maze*255, (reference_maze.shape[1], reference_maze.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    print(f"Elapsed time: {time()-start_time}")
    print(f"FPS: {iters / (time()-start_time)}")

    # cv2.imwrite("./images/output.png", maze_compressed)