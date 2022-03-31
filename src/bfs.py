from PIL import Image, ImageDraw
import numpy as np


def make_step(k, m, a): # TODO: optimize this? - don't be O(n^2)
  for i in range(len(m)):
    for j in range(len(m[i])):
      if m[i][j] == k:
        if i>0 and m[i-1][j] == 0 and a[i-1][j] == 0:
          m[i-1][j] = k + 1
        if j>0 and m[i][j-1] == 0 and a[i][j-1] == 0:
          m[i][j-1] = k + 1
        if i<len(m)-1 and m[i+1][j] == 0 and a[i+1][j] == 0:
          m[i+1][j] = k + 1
        if j<len(m[i])-1 and m[i][j+1] == 0 and a[i][j+1] == 0:
           m[i][j+1] = k + 1

def solve(a, start, end):
  m = []
  for i in range(len(a)):
      m.append([])
      for j in range(len(a[i])):
          m[-1].append(0)
  i,j = start
  m[i][j] = 1

  k = 0
  while m[end[0]][end[1]] == 0:
      k += 1
      make_step(k, m, a)
      if k > 300:
        print("solve failed")
        return None # failed

  i, j = end
  k = m[i][j]
  the_path = [(i,j)]
  while k > 1:
    if i > 0 and m[i - 1][j] == k-1:
      i, j = i-1, j
      the_path.append((i, j))
      k-=1
    elif j > 0 and m[i][j - 1] == k-1:
      i, j = i, j-1
      the_path.append((i, j))
      k-=1
    elif i < len(m) - 1 and m[i + 1][j] == k-1:
      i, j = i+1, j
      the_path.append((i, j))
      k-=1
    elif j < len(m[i]) - 1 and m[i][j + 1] == k-1:
      i, j = i, j+1
      the_path.append((i, j))
      k -= 1
  return the_path


def main():
  images = []
  # load numpy array (and switch convention - walls=1 empty=0)
  a = np.load('maze_small.npy').astype(int)
  a = a.tolist()
  for i in range(len(a)):
      for j in range(len(a[0])):
          a[i][j] = int(not a[i][j])

  # zoom = 20
  # borders = 6

  start = 1,1
  end = 10,10

  solution = solve(a, start, end)
  print(solution)


if __name__ == '__main__':
  main()
