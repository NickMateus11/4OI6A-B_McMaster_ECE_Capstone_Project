# import the necessary packages
import cv2
from image_test import maze_compression
from threading import Thread
from camera_flask_setup import VideoCamera
import time

class MazeThread:
	def __init__(self, video_stream:VideoCamera):
		self.count = 0

		self.x_grids = 8
		self.y_grids = 8
		self.wall_size = 4  # hard coded
		self.sensitivity = 0.85
		self.threshold = 30
		self.blur = 5
		self.adaptive_thresh = False
		
		self.video_stream = video_stream
		
		# img_name = "../images/maze_ball_trim.png"
		# self.img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)  # input
		# self.img = cv2.resize(self.img, (320, 240))
		# cv2.imwrite("imput.png", self.img)

		self.maze = None
		self.stopped = False

		self.start()

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
			img = self.video_stream.get_latest_frame(crop_region=(240,240))
			# img = self.img
			if img is not None:
				img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				new_maze, _ = maze_compression(
					img, 
					(self.y_grids, self.x_grids), 
					self.sensitivity, 
					preprocess={
						'thresh':self.threshold, 
						'blur':self.blur, 
						'adaptive':self.adaptive_thresh
					})
				self.maze = new_maze
				# self.count += 1

			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
			
			# time.sleep(0.1) # maze computes faster than necessary - TODO: synchronize this better

	def read_latest(self):
		return self.maze
	
	def get_maze_as_scaled_image(self):
		upscaled_maze = cv2.resize(
				self.read_latest()*255, 
				(self.video_stream.w, self.video_stream.h), 
				interpolation=cv2.INTER_NEAREST
			)		
		return upscaled_maze

	def stop(self):
		self.stopped = True
