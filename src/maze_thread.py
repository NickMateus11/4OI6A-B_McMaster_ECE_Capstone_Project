# import the necessary packages
import cv2
from image_test import maze_compression, preprocess_image
from threading import Thread
from camera_flask_setup import VideoCamera
import time

from colour_thresholding import locate_ball, locate_hazards

from image_utils import trim_maze_edge

class MazeThread:
	def __init__(self, video_stream:VideoCamera):
		self.count = 0

		self.x_grids = 8
		self.y_grids = 8
		self.sensitivity = 0.8
		self.threshold = 30
		self.blur = 3
		self.adaptive_thresh = True
		self.block = 45
		self.c = 18
		
		self.video_stream = video_stream

		self.maze = None
		self.ref_maze = None
		self.ball_position = None
		self.target_cell = None
		self.obstacles = None
		self.stopped = False

		self.update_maze()
		self.start()

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	def update_maze(self):
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
					},
					trim=True)
				self.maze = new_maze
				# self.ref_maze = ref_maze

	def update(self):
		# keep looping infinitely until the thread is stopped
		while (True):
			# grab the frame from the stream
			img = self.video_stream.get_latest_processed_frame()
			if img is not None:
				preprocess={
					'thresh':self.threshold, 
					'blur':self.blur, 
					"resize":1, 
					"block":self.block,
					"c":self.c, 
					'adaptive':self.adaptive_thresh
				}
				gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				self.ref_maze = preprocess_image(gray_img, **preprocess)

				# trim original image
				_, (start_col, end_col, start_row, end_row) = trim_maze_edge(self.ref_maze)
				img = img[start_col:end_col, start_row: end_row]

				(x,y), r, mask = locate_ball(img, (120,0,0), (255,255,255), convert_HSV=True)
				self.ball_position = None
				if (x and y):
					cx = int(x/img.shape[1] * (self.x_grids)) * 2 + 1
					cy = int(y/img.shape[0] * (self.y_grids)) * 2 + 1

					self.ball_position = (cx, cy)

				obstacles = locate_hazards(img, (50, 100, 45), (90, 255, 255), convert_HSV=True)
				self.obstacles = []
				if len(obstacles):
					for x,y in obstacles:
						cx = int(x/img.shape[1] * (self.x_grids)) * 2 + 1
						cy = int(y/img.shape[0] * (self.y_grids)) * 2 + 1

						self.obstacles.append( (cx,cy) )

			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return

	def read_latest(self):
		return self.maze.copy()
	
	def get_scaled_maze(self):
		maze = cv2.cvtColor(self.read_latest()*255, cv2.COLOR_GRAY2BGR)
		processed_h, processed_w = (min(self.video_stream.h, self.video_stream.w) , )*2

		if self.ball_position is not None:
			maze[self.ball_position[1], self.ball_position[0],:] = (0,255,0) 

		if self.target_cell is not None and list(maze[self.target_cell[1], self.target_cell[0],:]) != [0,0,0]:
			maze[self.target_cell[1], self.target_cell[0],:] = (128,0,128) 

		if self.obstacles is not None:
			for (x,y) in self.obstacles:
				maze[y,x,:] = (0,0,255)

		upscaled_maze = cv2.resize(maze, (processed_w, processed_h), interpolation=cv2.INTER_NEAREST)	

		return upscaled_maze

	def get_ref_image(self):
		if self.ref_maze is not None:
			return self.ref_maze.copy()

	def stop(self):
		self.stopped = True
