import cv2
import numpy as np

from image_utils import trim, draw_grid


def find_walls(arr, row, col, cell_size_y, cell_size_x, wall_size, sensitivity):
    check_buf = max(min(cell_size_x, cell_size_y) // 3, wall_size) 
    col_left = col
    col_right = col+cell_size_x
    row_top = row
    row_bottom = row+cell_size_y
    check_offset = int(max(min(cell_size_x, cell_size_y) / 2.5, wall_size))

    # print(np.average(arr[row_top : row_top+check_buf, col_left+check_offset : col_right-check_offset]))
    # try:
    #     cv2.imshow('test' , arr[row_top : row_top+check_buf , col_left+check_offset : col_right-check_offset] * 255)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    # except: pass

    top    = arr[row_top              : row_top+check_buf       , col_left+check_offset : col_right-check_offset]
    bottom = arr[row_bottom-check_buf : row_bottom              , col_left+check_offset : col_right-check_offset]
    left   = arr[row_top+check_offset : row_bottom-check_offset , col_left              : col_left+check_buf ]
    right  = arr[row_top+check_offset : row_bottom-check_offset , col_right-check_buf   : col_right          ]

    top_wall    = np.mean(top)    < sensitivity if top.size    else False
    bottom_wall = np.mean(bottom) < sensitivity if bottom.size else False
    left_wall   = np.mean(left)   < sensitivity if left.size   else False
    right_wall  = np.mean(right)  < sensitivity if right.size  else False
    
    return top_wall, bottom_wall, left_wall, right_wall

def maze_compression(img_name, grid_size, wall_size, sensitivity, do_blur_and_resize=False):
    (y_grids, x_grids) = grid_size

    img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
    if do_blur_and_resize:
        img = cv2.blur(img, (15,15))
        img = cv2.resize(img, (img.shape[1]//5, img.shape[0]//5))
    (thresh, bin_img) = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)

    trimmed_maze = trim(bin_img) // 255 # trim and normalize to 0s and 1s
    y_dim, x_dim = trimmed_maze.shape

    np.savetxt("maze.txt", trimmed_maze, fmt="%d")

    cell_size_x = x_dim//x_grids
    cell_size_y = y_dim//y_grids

    compressed_maze = np.ones( (2*y_grids+1, 2*x_grids+1) )
    for i in range(0, y_grids+1):
        for j in range(0, x_grids+1):
            top, bottom, left, right = \
                find_walls(trimmed_maze, i*cell_size_y, j*cell_size_x, cell_size_y, cell_size_x, wall_size, sensitivity)
            coord_mapping_y = 2*i + 1
            coord_mapping_x = 2*j + 1
            if top:
                try: compressed_maze[coord_mapping_y-1, coord_mapping_x] = 0
                except: pass
                try: compressed_maze[coord_mapping_y-1, coord_mapping_x-1] = 0
                except: pass
                try: compressed_maze[coord_mapping_y-1, coord_mapping_x+1] = 0
                except: pass
            if bottom:
                try: compressed_maze[coord_mapping_y+1, coord_mapping_x] = 0
                except: pass
                try: compressed_maze[coord_mapping_y+1, coord_mapping_x-1] = 0
                except: pass
                try: compressed_maze[coord_mapping_y+1, coord_mapping_x+1] = 0
                except: pass
            if left:
                try: compressed_maze[coord_mapping_y, coord_mapping_x-1] = 0
                except: pass
                try: compressed_maze[coord_mapping_y-1, coord_mapping_x-1] = 0
                except: pass
                try: compressed_maze[coord_mapping_y+1, coord_mapping_x-1] = 0
                except: pass
            if right:
                try: compressed_maze[coord_mapping_y, coord_mapping_x+1] = 0
                except: pass
                try: compressed_maze[coord_mapping_y-1, coord_mapping_x+1] = 0
                except: pass
                try: compressed_maze[coord_mapping_y+1, coord_mapping_x+1] = 0
                except: pass

    compressed_maze = compressed_maze.astype(np.uint8) # convert np array to valid cv2 image
    return compressed_maze, trimmed_maze*255


if __name__ == '__main__':
    x_grids = 6
    y_grids = 8
    wall_size = 4 #hard coded

    sensitivity = 0.83

    img_name = "./images/maze5.jpg"

    new_maze, reference_maze = maze_compression(img_name, (y_grids, x_grids), wall_size, sensitivity, do_blur_and_resize=True)

    draw_grid(reference_maze, y_grids, x_grids)
    cv2.imshow('image' , reference_maze)

    pixel_img = cv2.resize(new_maze*255, (reference_maze.shape[1],reference_maze.shape[0]), interpolation=cv2.INTER_NEAREST)
    cv2.imshow('output', pixel_img)

    np.save('maze_small', new_maze)

    cv2.waitKey(0)
    cv2.destroyAllWindows()