# import the necessary packages
import cv2
import numpy as np
from image_test import maze_compression
from threading import Thread
from pivideostream import PiVideoStream

class MazeThread:
	def __init__(self, video_stream:PiVideoStream):
		self.count = 0
		self.x_grids = 8
		self.y_grids = 8
		self.wall_size = 4  # hard coded
		self.sensitivity = 0.85
		self.video_stream = video_stream
		
		# img_name = "../images/maze_ball_trim.png"
		# self.img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)  # input
		# self.img = cv2.resize(self.img, (320, 240))
		# cv2.imwrite("imput.png", self.img)

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
			# grab the frame from the stream
			img = self.video_stream.read()
			# img = self.img
			if img is not None:
				img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				new_maze, _ = maze_compression(img, (self.y_grids, self.x_grids), self.wall_size, 
									self.sensitivity, preprocess={'thresh':30, 'blur':5, 'adaptive':False})
				self.maze = new_maze
				self.count += 1

			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return

	def read(self):
		# return the frame most recently read
		return self.maze

	def stop(self):
		# indicate that the thread should be stopped
		 
		self.stopped = True
