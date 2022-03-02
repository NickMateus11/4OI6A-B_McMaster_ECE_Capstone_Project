from imutils.video.pivideostream import PiVideoStream
import cv2
import time
import numpy as np

from fisheye_calib import undistort

class VideoCamera(object):
    def __init__(self, resolution=(320,240), sensor_mode=0, flip=False, correction=False, K=None, D=None):
        self.vs = PiVideoStream(resolution=resolution, 
                                sensor_mode=sensor_mode)
        self.w, self.h = resolution
        self.flip = flip

        # Fisheye Params
        self.fisheye_correction = correction
        if self.fisheye_correction:
            if K is None:
                self.K=np.array([[154.59426972365793, 0.0, 153.6848583692119], [0.0, 154.3517630161616, 107.27567776876337], [0.0, 0.0, 1.0]])
            if D is None:
                self.D=np.array([[-0.012920290356728127], [-0.0811284577051761], [0.0956426843995683], [-0.04483463666625924]])
        
        self.vs.start()
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def get_latest_frame(self, crop_region=None):
        frame = self.vs.read()
        
        if self.fisheye_correction:
            frame = undistort(frame, self.K, self.D, (frame.shape[1], frame.shape[0]))
        
        if crop_region is not None:
            crop_amount_w = self.w - crop_region[0] 
            crop_amount_h = self.h - crop_region[1]
            frame = frame[0+crop_amount_h//2: self.h-crop_amount_h//2,
                          0+crop_amount_w//2: self.w-crop_amount_w//2]
        
        return frame.copy()

