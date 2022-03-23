from imutils.video.pivideostream import PiVideoStream
import cv2
import time
import numpy as np

from fisheye_calib import undistort, undistort2
from colour_thresholding import locate_corners
from skew_correction import four_point_transform

class VideoCamera(object):
    def __init__(self, resolution=(320,240), sensor_mode=0, flip=False, 
                correction=False, K=None, D=None, 
                skew_fix=False, 
                crop_region=None):

        self.vs = PiVideoStream(resolution=resolution, 
                                sensor_mode=sensor_mode)
        self.w, self.h = resolution
        self.flip = flip

        self.crop_region = crop_region

        self.skew_fix = skew_fix
        self.lower_colour_bound = (0,128,0)
        self.upper_colour_bound = (100,255,100)

        # Fisheye Params
        self.fisheye_correction = correction
        if self.fisheye_correction:
            if max(resolution)<400:
                if K is None:
                    self.K=np.array([[154.59426972365793, 0.0, 153.6848583692119], [0.0, 154.3517630161616, 107.27567776876337], [0.0, 0.0, 1.0]])
                if D is None:
                    self.D=np.array([[-0.012920290356728127], [-0.0811284577051761], [0.0956426843995683], [-0.04483463666625924]])
            else:
                if K is None:
                    self.K=np.array([[302.74018036977867, 0.0, 304.9781913793884], [0.0, 301.11011450254375, 213.93634640718042], [0.0, 0.0, 1.0]])
                if D is None:
                    self.D=np.array([[-0.05759906030260242], [0.17803603968581097], [-0.31464705611716187], [0.1575447567212531]])

        
        self.vs.start()
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def get_latest_processed_frame(self):
        frame = self.get_latest_frame()
    
        if self.fisheye_correction:
            frame = undistort(frame, self.K, self.D, (frame.shape[1], frame.shape[0]))
        
        if self.crop_region is not None:
            crop_amount_w = self.w - self.crop_region[0] 
            crop_amount_h = self.h - self.crop_region[1]
            frame = frame[0+crop_amount_h//2: self.h-crop_amount_h//2,
                          0+crop_amount_w//2: self.w-crop_amount_w//2]

        if self.skew_fix:
            corners = locate_corners(frame, self.lower_colour_bound, self.upper_colour_bound)
            if len(corners)==4:
                frame = four_point_transform(frame, corners)

        return frame

    def get_latest_frame(self):     
        return self.vs.read().copy()

