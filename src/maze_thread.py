# import the necessary packages
import cv2
from image_test import maze_compression
from threading import Thread
from camera_flask_setup import VideoCamera
import time

from colour_thresholding import locate_ball

class MazeThread:
	def __init__(self, video_stream:VideoCamera):
		self.count = 0

		self.x_grids = 8
		self.y_grids = 8
		self.wall_size = 4  # hard coded
		self.sensitivity = 0.8
		self.threshold = 30
		self.blur = 3
		self.adaptive_thresh = True
		self.block = 45
		self.c = 18
		
		self.video_stream = video_stream
		
		# img_name = "../images/maze_ball_trim.png"
		# self.img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)  # input
		# self.img = cv2.resize(self.img, (320, 240))
		# cv2.imwrite("imput.png", self.img)

		self.maze = None
		self.ref_maze = None
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
			img = self.video_stream.get_latest_processed_frame()
			if img is not None:
				gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				new_maze, ref_maze = maze_compression(
					gray_img, 
					(self.y_grids, self.x_grids), 
					self.sensitivity, 
					preprocess={
						'thresh':self.threshold, 
						'blur':self.blur, 
						"resize":1, 
						"block":self.block,
						"c":self.c, 
						'adaptive':self.adaptive_thresh
					})
				self.maze = cv2.cvtColor(new_maze*255, cv2.COLOR_GRAY2BGR)
				self.ref_maze = ref_maze

				(x,y) = locate_ball(img, (0,128,0), (100,255,100))
				if (x and y):
					cx = int(x/img.shape[1] * (self.x_grids*2 + 1))
					cy = int(y/img.shape[0] * (self.y_grids*2 + 1))
					self.maze[cy,cx,:] = (0,255,0)

				# self.count += 1

			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
			
			# time.sleep(0.1) # maze computes faster than necessary - TODO: synchronize this better

	def read_latest(self):
		return self.maze.copy()
	
	def get_scaled_maze(self):
		upscaled_maze = cv2.resize(
				self.read_latest(), 
				(self.video_stream.w, self.video_stream.h), 
				interpolation=cv2.INTER_NEAREST
			)		
		return upscaled_maze

	def get_ref_image(self):
		return self.ref_maze.copy()

	def stop(self):
		self.stopped = True
