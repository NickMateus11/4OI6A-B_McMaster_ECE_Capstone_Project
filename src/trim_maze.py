import numpy as np
from scipy import stats


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

def trim(arr):
    start_row = 0
    while 0 not in arr[start_row]:
        start_row += 1

    end_row = len(arr)-1
    while end_row > start_row and 0 not in arr[end_row]:
        end_row -= 1

    start_cols = []
    end_cols = []
    for i in range(start_row, end_row+1):
        try:
            bounds = np.where(arr[i] == 0)[0]
            start_cols.append(bounds[0])
            end_cols.append(bounds[-1])
        except: continue
    start_col = stats.mode(start_cols).mode[0]
    end_col =  stats.mode(end_cols).mode[0]

    trimmed_arr = arr[start_row:end_row+1, start_col:end_col+1] // 255 # normalize to 0s and 1s
    return trimmed_arr