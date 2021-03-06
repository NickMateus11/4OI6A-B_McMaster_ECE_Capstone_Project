import numpy as np
import statistics
import cv2


def draw_grid(img, rows, cols, thickness=1, x_offset=0, y_offset=0):
    h, w = img.shape[0], img.shape[1]

    # draw vertical lines
    for x in np.linspace(start=0+x_offset, stop=w-x_offset, num=cols+1):
        x = int(round(x))
        cv2.line(img, (x, 0+y_offset), (x, h-y_offset), color=(128,)*3, thickness=thickness)

    # draw horizontal lines
    for y in np.linspace(start=0+y_offset, stop=h-y_offset, num=rows+1):
        y = int(round(y))
        cv2.line(img, (0+x_offset, y), (w-x_offset, y), color=(128,)*3, thickness=thickness)


def trim_file(filename):
    with open(filename) as f:
        file_contents = f.read().split()

    start_row = 0
    while '#' not in file_contents[start_row]:
        start_row += 1
    file_contents = file_contents[start_row:]

    row = 0
    while row < len(file_contents) and '#' in file_contents[row]:
        row += 1
    file_contents = file_contents[:row]

    start_col = file_contents[start_row].index('#')
    end_col = len(file_contents[start_row]) - ''.join(reversed(file_contents[start_row])).index('#') - 1
    for r in range(len(file_contents)):
        file_contents[r] = file_contents[r][start_col:end_col+1]

    with open('maze_trim.txt', 'w') as f:
        for r in file_contents:
            f.write(r)
            f.write('\n')


def trim_maze_edge(arr):
    start_cols = []
    end_cols   = []
    for i in range(len(arr)):
        try:
            bounds = np.where(arr[i] == 0)[0]
            start_cols.append(bounds[0])
            end_cols.append(bounds[-1])
        except: continue
    try:
        start_col = statistics.mode(start_cols)
        end_col   = statistics.mode(end_cols)
    except statistics.StatisticsError:
        start_col = 0
        end_col = len(arr[0])

    start_rows = []
    end_rows   = []
    for i in range(len(arr[0])):
        try:
            bounds = np.where(arr[:,i] == 0)[0]
            start_rows.append(bounds[0])
            end_rows.append(bounds[-1])
        except: continue
    
    try:
        start_row = statistics.mode(start_rows)
        end_row   = statistics.mode(end_rows)
    except statistics.StatisticsError:
        start_row = 0
        end_row = len(arr)

    trimmed_arr = arr[start_row:end_row, start_col:end_col]
    return trimmed_arr, (start_col, end_col, start_row, end_row)