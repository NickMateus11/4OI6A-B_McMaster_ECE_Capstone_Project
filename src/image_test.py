import cv2
import numpy as np

from trim_maze import trim

def draw_grid(img, rows, cols):
    h, w = img.shape

    # draw vertical lines
    for x in np.linspace(start=0, stop=w, num=cols+1):
        x = int(round(x))
        cv2.line(img, (x, 0), (x, h), color=(0,0,0), thickness=1)

    # draw horizontal lines
    for y in np.linspace(start=0, stop=h, num=rows+1):
        y = int(round(y))
        cv2.line(img, (0, y), (w, y), color=(0,0,0), thickness=1)


img_name = "./images/maze5.jpg"

img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)

img = cv2.blur(img, (15,15))
img = cv2.resize(img, (img.shape[0]//5, img.shape[1]//5))

# (thresh, bin_img) = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
(thresh, bin_img) = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)

with open('maze.txt', 'w') as f:
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            f.write('^' if bin_img[i,j] else '#')
        f.write('\n')

trimmed_maze = trim(bin_img)
np.savetxt("maze.txt", trimmed_maze, fmt="%d")
y_dim, x_dim = trimmed_maze.shape

# cv2.imshow('OG'    , img)
# cv2.imshow('image' , trimmed_maze*255)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

#horizontal scanning
# sample_res = 16
# min_cell_gap_x = x_dim
# wall_flag = True
# for i in range(y_dim-sample_res):
#     curr_cell_gap = 0
#     for j in range(x_dim-sample_res):
#         if np.mean(trimmed_maze[i:i+sample_res,j:j+sample_res]) > 0.9:
#             wall_flag = False
#             curr_cell_gap += 1
#         else:
#             wall_flag = True
#             # print(curr_cell_gap)
#             if curr_cell_gap < min_cell_gap_x and curr_cell_gap > sample_res:
#                 min_cell_gap_x = curr_cell_gap
#             curr_cell_gap = 0
#     # print(min_cell_gap_x)
# print("Cell size: ", min_cell_gap_x)

#vertical scanning
# min_cell_gap_y = org_dim[0]
# for j in range(org_dim[1]):
#     for i in range(org_dim[0]):

x_grids = 6
y_grids = 8

cell_size_x = x_dim//x_grids
cell_size_y = y_dim//y_grids

done = False
idx = 0
while (not done):
    done = trimmed_maze[idx, idx] == 1
    idx += 1
print(idx)
wall_size = idx

# wall_size = 4 #hard coded

# dim = bin_img.shape
# small_img = cv2.resize(bin_img, (dim[0]//5, dim[1]//5))
# pixel_img = cv2.resize(small_img, dim, interpolation=cv2.INTER_NEAREST)

# # cv2.imshow('OG'    , img)
# cv2.imshow('image' , bin_img)

# # # cv2.imshow('image2', small_img)
# # cv2.imshow('image3', pixel_img)

# cv2.waitKey(0)
# cv2.destroyAllWindows()


'''
pass the grid square over the image, measure the density of black or white pixels
if above some threshold call the grid square a wall or empty
move grid square over by its length and check again - repeat
'''

def find_walls(arr, row, col, cell_size_y, cell_size_x, wall_size):
    sensitivity = 0.83  # higher is more sensitive

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

    top    = np.average(arr[row_top              : row_top+check_buf       , col_left+check_offset : col_right-check_offset]) < sensitivity
    bottom = np.average(arr[row_bottom-check_buf : row_bottom              , col_left+check_offset : col_right-check_offset]) < sensitivity
    left   = np.average(arr[row_top+check_offset : row_bottom-check_offset , col_left              : col_left+check_buf ])    < sensitivity
    right  = np.average(arr[row_top+check_offset : row_bottom-check_offset , col_right-check_buf   : col_right          ])    < sensitivity
    return top, bottom, left, right

compressed_maze = np.ones( (2*y_grids+1, 2*x_grids+1) )
for i in range(0, y_grids+1):
    for j in range(0, x_grids+1):
        top, bottom, left, right = find_walls(trimmed_maze, i*cell_size_y, j*cell_size_x, cell_size_y, cell_size_x, wall_size)
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


draw_grid(trimmed_maze, y_grids, x_grids)
cv2.imshow('image' , trimmed_maze*255)

pixel_img = cv2.resize(compressed_maze, trimmed_maze.shape, interpolation=cv2.INTER_NEAREST)
cv2.imshow('output', pixel_img)
with open('maze_test.txt','w') as f:
    for i in range(compressed_maze.shape[0]):
        for j in range(compressed_maze.shape[1]):
            f.write('^' if compressed_maze[i,j] else '#')
        f.write('\n')

np.save('maze_small', compressed_maze)

cv2.waitKey(0)
cv2.destroyAllWindows()

