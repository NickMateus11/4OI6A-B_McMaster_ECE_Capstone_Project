
# from imutils.video.pivideostream import PiVideoStream
from pivideostream import PiVideoStream # custom library modification

import argparse
import time
import cv2

from maze_thread import MazeThread 


def main(args):
	# initialize the camera and stream
	print("[INFO] sampling THREADED frames from `picamera` module...")
	video_stream = PiVideoStream(resolution=(320, 240))
	maze_stream = MazeThread(video_stream)

	video_stream.start()
	maze_stream.start()

	start_time = time.time()
	while time.time()-start_time < args["time"]:
		# grab the frame from the threaded video stream
		frame = video_stream.read() 
		# frame = imutils.resize(frame, width=400)

		# grab latest maze compression img
		# TODO: event system? only grab when new frame ready
		maze = maze_stream.read()

		time.sleep(1)
	
	# stop the timer and display FPS information
	video_stream.stop()
	maze_stream.stop()

	maze = cv2.resize(maze*255, (320, 240), interpolation=cv2.INTER_NEAREST)
	cv2.imwrite("output.png", maze)

	print(f"Maze fps:\t{maze_stream.count/(time.time()-start_time)}")
	print(f"Video fps:\t{video_stream.frame_count/(time.time()-start_time)}")


if __name__ == '__main__':
	# construct the argument parse and parse the arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--time", type=int, default=5, help="# of frames to loop over for FPS test")
	args = vars(parser.parse_args())

	main(args)