import cv2

from image_utils import draw_grid
from image_test import maze_compression
from bfs import solve

# from gpiozero import Servo
# import pigpio
# import time

# SERVO_PIN_1 = 25
# SERVO_PIN_2 = 24

# pwm = pigpio.pi()
# pwm.set_mode(SERVO_PIN_1, pigpio.OUTPUT)
# pwm.set_PWM_frequency(SERVO_PIN_1, 50)
# pwm.set_mode(SERVO_PIN_2, pigpio.OUTPUT)
# pwm.set_PWM_frequency(SERVO_PIN_2, 50)


def coord_to_grid_cell(x, y, img_dim_y, img_dim_x, grid_y, grid_x):

    x_cell = int(x // (img_dim_x / grid_x))
    y_cell = int(y // (img_dim_y / grid_y))

    return y_cell, x_cell


def click_and_mark(event, x, y, flags, param):
    if event in [cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN]:
        # unpack params
        image, image_copy, grids, end_rect, start_rect = param
        grid_y, grid_x = grids

        img_dim_y, img_dim_x = image_copy.shape[0], image_copy.shape[1]

        # calc grid cell
        y_cell, x_cell = coord_to_grid_cell(
            x, y, img_dim_y, img_dim_x, grid_y, grid_x)

        x_start = int(x_cell * (img_dim_x / grid_x))
        y_start = int(y_cell * (img_dim_y / grid_y))
        x_end = int(x_start + (img_dim_x / grid_x))
        y_end = int(y_start + (img_dim_y / grid_y))

        # copy and overwrite image
        image_copy[:] = image.copy()

        # draw start cell
        if event == cv2.EVENT_LBUTTONDOWN:
            if sum(image_copy[y, x]) > 0:  # not a wall
                start_rect[:] = [(x_start, y_start), (x_end, y_end)]
            cv2.rectangle(
                image_copy, start_rect[0], start_rect[1], (0, 255, 0), 4)
            if end_rect and not end_rect == start_rect:
                cv2.rectangle(
                    image_copy, end_rect[0], end_rect[1], (180, 100, 255), 4)
            else:
                end_rect[:] = []
        # draw end cell
        elif event == cv2.EVENT_RBUTTONDOWN:
            if sum(image_copy[y, x]) > 0:  # not a wall
                end_rect[:] = [(x_start, y_start), (x_end, y_end)]
            cv2.rectangle(
                image_copy, end_rect[0], end_rect[1], (180, 100, 255), 4)
            if start_rect and not end_rect == start_rect:
                cv2.rectangle(
                    image_copy, start_rect[0], start_rect[1], (0, 255, 0), 4)
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
        cv2.circle(img, (x_coord, y_coord), int(
            min(spacing_x, spacing_y)/4), (0, 0, 255), -1)


def main():
    start_rect = []
    end_rect = []

    grid_x = 8
    grid_y = 8

    # compress maze image
    image_name = "./images/maze5.jpg"
    image_name = "./images/maze_ball_trim.png"
    img = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)  # input
    maze, ref_img = maze_compression(img, (grid_y, grid_x), 0.83, preprocess={
                                     'thresh': 55, 'blur': 15, 'resize': 2})

    image = cv2.cvtColor(maze*255, cv2.COLOR_GRAY2BGR)
    image = cv2.resize(
        image, (ref_img.shape[1], ref_img.shape[0]), interpolation=cv2.INTER_NEAREST)

    img_dim_y, img_dim_x = image.shape[0], image.shape[1]

    # swap convention - 0s and 1s switch
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            maze[i][j] = int(not maze[i][j])

    draw_grid(image, grid_y*2+1, grid_x*2+1)

    win_name = "image"
    cv2.imshow(win_name, image)

    image_copy = image.copy()
    cv2.setMouseCallback(win_name, click_and_mark,
                         param=[image, image_copy, (grid_y*2+1, grid_x*2+1), end_rect, start_rect])
    solution = []
    prev_solution = None
    # start_rect = [(36, 36), (72, 72)]
    # end_rect = [(36, 73), (72, 109)]
    while (True):
        cv2.imshow(win_name, image_copy)

        # start and end exist
        if len(start_rect) and len(end_rect):
            start = ((start_rect[0][0] + start_rect[1][0]) //
                     2, (start_rect[0][1] + start_rect[1][1]) // 2)
            end = ((end_rect[0][0] + end_rect[1][0]) // 2,
                   (end_rect[0][1] + end_rect[1][1]) // 2)
            # with the overlay
            solution = solve(maze,
                             start=coord_to_grid_cell(
                                 *start, *(image.shape[:2]), grid_y*2+1, grid_x*2+1),
                             end=coord_to_grid_cell(*end, *(image.shape[:2]), grid_y*2+1, grid_x*2+1))
            draw_path(image_copy, solution, (grid_y*2+1, grid_x*2+1))

            # # hardcode
            # solution = solve(maze,
            #                  start=(1, 1),
            #                  end=(15, 15))

            solution_rev = solution[::-1]
            if prev_solution != solution:
                servo_move(solution_rev)
        key = cv2.waitKey(1) & 0xFF
        prev_solution = solution
        if key == 27:
            break
        if not cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE):
            break
    cv2.destroyAllWindows()


def servo_move(path):
    moves = []
    test = []
    test2 = []
    v_move = 0
    h_move = 0
    moves.append(("none", "none"))
    for i in range(0, len(path)-1):
        pointer1 = path[i][::-1]
        pointer2 = path[i+1][::-1]
        if pointer1[0] < pointer2[0]:
            h_move = "right"
        elif pointer1[0] > pointer2[0]:
            h_move = "left"
        else:
            h_move = "none"
        if pointer1[1] < pointer2[1]:
            v_move = "down"
        elif pointer1[1] > pointer2[1]:
            v_move = "up"
        else:
            v_move = "none"
        moves.append((h_move, v_move))
    moves.append(("none", "none"))
    print(moves)
    for j in range(len(moves)-1):
        if (moves[j][0] != moves[j+1][0]) and (moves[j][1] != moves[j+1][1]):
            print("transition at move:", j, "from direction:", moves[j][0] if moves[j][1] == "none" else moves[j][1], ", to direction:",
                  moves[j+1][0] if moves[j+1][1] == "none" else moves[j+1][1])
            test.append((j, moves[j][0] if moves[j][1]
                         == "none" else moves[j][1]))
    test.append((j, moves[j][0] if moves[j][1]
                 == "none" else moves[j][1]))
    print(test)
    if test != []:
        test2.append((test[0][0]-0, test[0][1]))
        for k in range(len(test)-1):
            test2.append((test[k+1][0]-test[k][0], test[k+1][1]))
        print("steps from start to end are:", test2)

    # for i in range(len(test2)):
    #     print(i,test2[i][1])
    #     if test2[i][1] == 'down':
    #         pwm.set_servo_pulsewidth(SERVO_PIN_2, 1000)
    #         time.sleep(3)
    #     elif test2[i][1] == 'up':
    #         pwm.set_servo_pulsewidth(SERVO_PIN_2, 2000)
    #         time.sleep(3)
    #     elif test2[i][1] == 'right':
    #         pwm.set_servo_pulsewidth(SERVO_PIN_1, 1000)
    #         time.sleep(3)
    #     else:
    #         pwm.set_servo_pulsewidth(SERVO_PIN_1, 2000)
    #         time.sleep(3)


if __name__ == '__main__':
    main()
