import cv2
import numpy as np

from image_utils import trim_maze_edge, draw_grid


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

    top = arr[row_top: row_top+check_buf, col_left +
              check_offset: col_right-check_offset]
    bottom = arr[row_bottom-check_buf: row_bottom,
                 col_left+check_offset: col_right-check_offset]
    left = arr[row_top+check_offset: row_bottom -
               check_offset, col_left: col_left+check_buf]
    right = arr[row_top+check_offset: row_bottom -
                check_offset, col_right-check_buf: col_right]

    top_wall = np.mean(top) < sensitivity if top.size else False
    bottom_wall = np.mean(bottom) < sensitivity if bottom.size else False
    left_wall = np.mean(left) < sensitivity if left.size else False
    right_wall = np.mean(right) < sensitivity if right.size else False

    return top_wall, bottom_wall, left_wall, right_wall


def preprocess_image(img, blur=1, thresh=150, resize=1, block=9, c=2, adaptive=False):
    # order matters
    img = cv2.blur(img, (blur,blur))
    img = cv2.resize(img, (img.shape[1]//resize, img.shape[0]//resize))
    if adaptive:
        bin_img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, c)
    else:
        (_, bin_img) = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)
    return bin_img


def maze_compression(img, grid_size, wall_size, sensitivity, preprocess=None, trim=False):
    (y_grids, x_grids) = grid_size

    if preprocess:
        img = preprocess_image(img, **preprocess)

    # TODO: remove trimming - doesn't work well with real-world images
    if trim:
        trimmed_maze = trim_maze_edge(img) // 255  # trim and normalize to 0s and 1s
    else: 
        trimmed_maze = img // 255
    y_dim, x_dim = trimmed_maze.shape[:2]

    # np.savetxt("maze.txt", trimmed_maze, fmt="%d")

    cell_size_x = x_dim//x_grids
    cell_size_y = y_dim//y_grids

    compressed_maze = np.ones((2*y_grids+1, 2*x_grids+1))
    for i in range(0, y_grids+1):
        for j in range(0, x_grids+1):
            top, bottom, left, right = \
                find_walls(trimmed_maze, i*cell_size_y, j*cell_size_x,
                           cell_size_y, cell_size_x, wall_size, sensitivity)
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

    compressed_maze = compressed_maze.astype(np.uint8)  # convert np array to valid cv2 image
    return compressed_maze, trimmed_maze*255


if __name__ == '__main__':
    x_grids = 8
    y_grids = 8
    wall_size = 4  # hard coded

    sensitivity = 0.53

    img_name = "./images/maze_uncropped.png"
    img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)  # input

    new_maze, reference_maze = maze_compression(img, (y_grids, x_grids), wall_size, sensitivity, trim=True,
                        preprocess={'block': 255, 'blur':15, 'resize':5, 'adaptive':True})

    draw_grid(reference_maze, y_grids, x_grids)
    cv2.imshow('image', reference_maze)

    pixel_img = cv2.resize(
        new_maze*255, (reference_maze.shape[1], reference_maze.shape[0]), interpolation=cv2.INTER_NEAREST)
    cv2.imshow('output', pixel_img)

    np.save('maze_small', new_maze)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
