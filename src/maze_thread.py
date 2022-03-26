# import the necessary packages
import cv2
from image_test import maze_compression, preprocess_image
from threading import Thread
from camera_flask_setup import VideoCamera
import time

from colour_thresholding import locate_ball

from image_utils import trim_maze_edge

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
		self.ball_position = None
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
				self.maze = cv2.cvtColor(new_maze*255, cv2.COLOR_GRAY2BGR)
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
				_, crop_vals = trim_maze_edge(self.ref_maze) 

				# trim image to reflect how to maze is going to be processed - so ball tracking is accurate
				(start_col, end_col, start_row, end_row) = crop_vals
				trimmed_img = img[start_row:end_row, start_col:end_col]
				(x,y), r, mask = locate_ball(trimmed_img, (120,0,0), (255,255,255), convert_HSV=True)
				if (x and y):
					# cx = int(x/img.shape[1] * (self.x_grids*2 + 1))
					# cy = int(y/img.shape[0] * (self.y_grids*2 + 1))
					cx = int(x/trimmed_img.shape[1] * (self.x_grids)) * 2 + 1
					cy = int(y/trimmed_img.shape[0] * (self.y_grids)) * 2 + 1

					self.ball_position = (cx, cy)
					# self.maze[cy,cx,:] = (0,255,0)

				# self.count += 1

			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
			
			# time.sleep(0.1) # maze computes faster than necessary - TODO: synchronize this better

	def read_latest(self):
		return self.maze.copy()
	
	def get_scaled_maze(self, include_ball=True):
		maze = self.read_latest()
		processed_h, processed_w = self.video_stream.get_latest_processed_frame().shape[:2]
		if include_ball and self.ball_position is not None:
			maze[self.ball_position[1], self.ball_position[0],:] = (0,255,0) 
		upscaled_maze = cv2.resize(maze, (processed_w, processed_h), interpolation=cv2.INTER_NEAREST)		
		return upscaled_maze

	def get_ref_image(self):
		return self.ref_maze.copy()

	def stop(self):
		self.stopped = True
