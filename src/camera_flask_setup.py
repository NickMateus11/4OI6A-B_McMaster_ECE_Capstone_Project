import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np

from fisheye_calib import undistort
from image_utils import draw_grid


class VideoCamera(object):
    def __init__(self, resolution=(320,240), sensor_mode=0, flip=False):
        self.vs = PiVideoStream(resolution=resolution, 
                                sensor_mode=sensor_mode)
        self.w, self.h = resolution
        self.flip = flip

        # Fisheye Params
        # self.DIM=(320, 240)
        # self.K=np.array([[154.88223395934025, 0.0, 152.79592302342448], [0.0, 154.70519413336302, 107.41300113111684], [0.0, 0.0, 1.0]])
        # self.D=np.array([[-0.023124661972220774], [-0.01846311275378898], [-0.005734648752030648], [0.0012054217338599944]])
        self.K=np.array([[154.51701484112385, 0.0, 154.10226948267444], [0.0, 154.76218384046956, 107.72921167218352], [0.0, 0.0, 1.0]])
        self.D=np.array([[0.016063479457645552], [-0.27340196746363876], [0.680724084158881], [-0.572518845031667]])
        
        self.vs.start()
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    # def flip_if_needed(self, frame):
    #     if self.flip:
    #         return np.flip(frame, 0)
    #     return frame

    def get_frame(self, fisheye_correction=True, crop_dim=None):
        frame = self.vs.read()

        if crop_dim is None:
            crop_dim = self.w, self.h
        crop_amount_w = self.w - crop_dim[0] 
        crop_amount_h = self.h - crop_dim[1]
        frame = frame[0+crop_amount_h//2: self.h-crop_amount_h//2,
                      0+crop_amount_w//2: self.w-crop_amount_w//2]
            
        if fisheye_correction:
            frame = undistort(frame, self.K, self.D, (frame.shape[1], frame.shape[0]))
        
        draw_grid(frame, 8,8)
        
        return frame

