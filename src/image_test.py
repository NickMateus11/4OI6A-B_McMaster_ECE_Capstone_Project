import cv2
import numpy as np

from image_utils import trim_maze_edge, draw_grid


def find_walls(arr, row, col, cell_size_y, cell_size_x, sensitivity):
    col_left = int(col)
    col_right = int(col+cell_size_x)
    row_top = int(row)
    row_bottom = int(row+cell_size_y)
    check_offset_width = int(max(min(cell_size_x, cell_size_y) / 4, 1))
    check_offset_depth = int(max(min(cell_size_x, cell_size_y) / 3, 1))
    c_x = int(cell_size_x//2)
    c_y = int(cell_size_y//2)

    top    = arr[row_top: row_top+check_offset_depth, 
                col_left+c_x-check_offset_width//2: col_right-c_x+check_offset_width//2]
    bottom = arr[row_bottom-check_offset_depth: row_bottom,
                col_left+c_x-check_offset_width//2: col_right-c_x+check_offset_width//2]
    left   = arr[row_top+c_y-check_offset_width//2: row_bottom-c_y+check_offset_width//2, 
                col_left: col_left+check_offset_depth]
    right  = arr[row_bottom-c_y-check_offset_width//2: row_bottom-c_y+check_offset_width//2, 
                col_right-check_offset_depth: col_right]

    # print(np.average(arr[row_top : row_top+check_buf, col_left+check_offset_width : col_right-check_offset_width]))
    # try:
    #     cv2.imshow('test' , cv2.resize(top * 255, (100,100)))
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    # except: pass

    top_wall    = np.mean(top)    < sensitivity if top.size else False
    bottom_wall = np.mean(bottom) < sensitivity if bottom.size else False
    left_wall   = np.mean(left)   < sensitivity if left.size else False
    right_wall  = np.mean(right)  < sensitivity if right.size else False

    return top_wall, bottom_wall, left_wall, right_wall


def preprocess_image(img, blur=1, thresh=150, resize=1, block=9, c=2, adaptive=False):
    # order matters
    img = cv2.GaussianBlur(img, (blur,blur), 0)
    # img = cv2.bilateralFilter(img, 5, blur, blur)
    # img = cv2.blur(img, (blur,blur))
    img = cv2.resize(img, (img.shape[1]//resize, img.shape[0]//resize))
    if adaptive:
        bin_img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, c)
    else:
        (_, bin_img) = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)
        # (_, bin_img) = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return bin_img


def maze_compression(img, grid_size, sensitivity, preprocess=None, trim=False):
    (y_grids, x_grids) = grid_size

    if preprocess:
        img = preprocess_image(img, **preprocess)

    # TODO: remove trimming - doesn't work well with real-world images
    if trim:
        trimmed_maze, _ = trim_maze_edge(img) # trim and normalize to 0s and 1s
        trimmed_maze = trimmed_maze // 255 
    else: 
        trimmed_maze = img // 255
    y_dim, x_dim = trimmed_maze.shape[:2]

    # np.savetxt("maze.txt", trimmed_maze, fmt="%d")

    cell_size_x = x_dim/x_grids
    cell_size_y = y_dim/y_grids

    compressed_maze = np.ones((2*y_grids+1, 2*x_grids+1))
    for i in range(0, y_grids+1):
        for j in range(0, x_grids+1):
            top, bottom, left, right = \
                find_walls(trimmed_maze, i*cell_size_y, j*cell_size_x,
                           cell_size_y, cell_size_x, sensitivity)
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

    sensitivity = 0.80

    img_name = "./images/pi_camera_capture.jpg"
    img = cv2.imread(img_name)  # input
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    new_maze, reference_maze = maze_compression(img, (y_grids, x_grids), sensitivity,
                        preprocess={'block': 45, 'blur':3, 'resize':1, 'adaptive':True, 'c':18})

    draw_grid(reference_maze, y_grids, x_grids)
    cv2.imshow('image', reference_maze)

    pixel_img = cv2.resize(
        new_maze*255, (reference_maze.shape[1], reference_maze.shape[0]), interpolation=cv2.INTER_NEAREST)
    cv2.imshow('output', pixel_img)

    np.save('maze_small', new_maze)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # cv2.imwrite("test.png", reference_maze)
