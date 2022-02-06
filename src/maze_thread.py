# import the necessary packages
import cv2
import numpy as np
from image_test import maze_compression
from threading import Thread

class MazeThread:
	def __init__(self):
		self.count = 0
		self.x_grids = 8
		self.y_grids = 8
		self.wall_size = 4  # hard coded
		self.sensitivity = 0.53
		img_name = "./images/maze_ball_trim.png"
		self.img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)  # input
		self.maze = None
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		while (True):
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			new_maze, reference_maze = maze_compression(self.img, (self.y_grids, self.x_grids), self.wall_size, self.sensitivity,preprocess={'block': 255, 'blur':15, 'resize':5, 'adaptive':True})
			self.maze = new_maze
			self.count += 1
			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				return

	def read(self):
		# return the frame most recently read
		return self.maze

	def stop(self):
		# indicate that the thread should be stopped
		 
		self.stopped = True
