import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np

from fisheye_calib import undistort


class VideoCamera(object):
    def __init__(self, resolution=(320,240), sensor_mode=0, flip=False):
        self.vs = PiVideoStream(resolution=resolution, 
                                sensor_mode=sensor_mode)
        self.w, self.h = resolution
        self.flip = flip

        # Fisheye Params
        # self.DIM=(320, 240)
        self.K=np.array([[154.88223395934025, 0.0, 152.79592302342448], [0.0, 154.70519413336302, 107.41300113111684], [0.0, 0.0, 1.0]])
        self.D=np.array([[-0.023124661972220774], [-0.01846311275378898], [-0.005734648752030648], [0.0012054217338599944]])
        
        self.vs.start()
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    # def flip_if_needed(self, frame):
    #     if self.flip:
    #         return np.flip(frame, 0)
    #     return frame

    def get_frame(self, fisheye_correction=True):
        frame = self.vs.read()
        if fisheye_correction:
            frame = undistort(frame, self.K, self.D, (self.w,self.h))
        return frame

