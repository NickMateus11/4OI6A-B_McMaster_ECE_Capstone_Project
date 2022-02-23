import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np

class VideoCamera(object):
    def __init__(self, resolution=(320,240), sensor_mode=0, flip=False):
        self.vs = PiVideoStream(resolution=resolution, 
                                sensor_mode=sensor_mode)
        self.w, self.h = resolution
        self.flip = flip
        
        self.vs.start()
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    # def flip_if_needed(self, frame):
    #     if self.flip:
    #         return np.flip(frame, 0)
    #     return frame

    def get_frame(self):
        frame = self.vs.read()
        # frame = self.flip_if_needed(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
