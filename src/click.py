import cv2

from image_utils import draw_grid
from image_test import maze_compression
from bfs import solve

def coord_to_grid_cell(x, y, img_dim_y, img_dim_x, grid_y, grid_x):

    x_cell =  int(x // (img_dim_x / grid_x))
    y_cell =  int(y // (img_dim_y / grid_y))

    return y_cell, x_cell


def click_and_mark(event, x, y, flags, param):
    if event in [cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN]:
        # unpack params
        image, image_copy, grids, end_rect, start_rect = param
        grid_y, grid_x = grids
        
        img_dim_y, img_dim_x = image_copy.shape[0], image_copy.shape[1]
        
        # calc grid cell
        y_cell, x_cell = coord_to_grid_cell(x, y, img_dim_y, img_dim_x, grid_y, grid_x)

        x_start = int(x_cell   * (img_dim_x / grid_x))
        y_start = int(y_cell   * (img_dim_y / grid_y))
        x_end   = int(x_start  + (img_dim_x / grid_x)) 
        y_end   = int(y_start  + (img_dim_y / grid_y))

        # copy and overwrite image
        image_copy[:] = image.copy()
        
        # draw start cell
        if event == cv2.EVENT_LBUTTONDOWN:
            if sum(image_copy[y,x])>0: # not a wall
                start_rect[:] = [(x_start, y_start) , (x_end, y_end)]
            cv2.rectangle(image_copy, start_rect[0], start_rect[1], (0, 255, 0), 4)
            if end_rect and not end_rect == start_rect:
                cv2.rectangle(image_copy, end_rect[0], end_rect[1], (180, 100, 255), 4)
            else: 
                end_rect[:] = []
        # draw end cell
        elif event == cv2.EVENT_RBUTTONDOWN:
            if sum(image_copy[y,x])>0: # not a wall
                end_rect[:] = [(x_start, y_start) , (x_end, y_end)]
            cv2.rectangle(image_copy, end_rect[0], end_rect[1], (180, 100, 255), 4)
            if start_rect and not end_rect == start_rect:
                cv2.rectangle(image_copy, start_rect[0], start_rect[1], (0, 255, 0), 4)
            else: 
                start_rect[:] = []


def draw_path(img, path, grid):
    grid_y, grid_x = grid
    y_dim, x_dim = img.shape[:2]

    spacing_y = y_dim/grid_y
    spacing_x = x_dim/grid_x

    for grid_coord in path:
        y_coord = int(grid_coord[0] * spacing_y + spacing_y/2)
        x_coord = int(grid_coord[1] * spacing_x + spacing_x/2)
        cv2.circle(img, (x_coord, y_coord), int(min(spacing_x,spacing_y)/4), (0, 0, 255), -1)

def main():
    start_rect = []
    end_rect = []

    grid_x = 11
    grid_y = 11

    # compress maze image
    maze, ref_img = maze_compression("./images/maze0.jpg", (grid_y, grid_x), 4, 0.83)

    image = cv2.cvtColor(maze*255, cv2.COLOR_GRAY2BGR)
    image = cv2.resize(image, (ref_img.shape[1]*2,ref_img.shape[0]*2), interpolation=cv2.INTER_NEAREST)

    img_dim_y, img_dim_x = image.shape[0], image.shape[1]

    # swap convention - 0s and 1s switch
    for i in range(len(maze)):
      for j in range(len(maze[0])):
          maze[i][j] = int(not maze[i][j])

    draw_grid(image, grid_y*2+1, grid_x*2+1)

    win_name = "image"
    cv2.imshow(win_name, image)

    image_copy = image.copy()
    cv2.setMouseCallback(win_name, click_and_mark, \
        param=[image, image_copy, (grid_y*2+1, grid_x*2+1), end_rect, start_rect])

    while (True):
        cv2.imshow(win_name, image_copy)

        # start and end exist
        if len(start_rect) and len(end_rect): # TODO: don't re-solve maze if endpoints remain the same
            start = ((start_rect[0][0] + start_rect[1][0]) // 2 , (start_rect[0][1] + start_rect[1][1]) // 2)
            end = ((end_rect[0][0] + end_rect[1][0]) // 2 , (end_rect[0][1] + end_rect[1][1]) // 2)
            solution = solve(maze, \
                start=coord_to_grid_cell(*start, *(image.shape[:2]), grid_y*2+1, grid_x*2+1), \
                end=coord_to_grid_cell(*end, *(image.shape[:2]), grid_y*2+1, grid_x*2+1))
            draw_path(image_copy, solution, (grid_y*2+1, grid_x*2+1))

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        if not cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE):        
            break        

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
