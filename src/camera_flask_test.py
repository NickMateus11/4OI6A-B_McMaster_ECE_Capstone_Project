from flask import Flask, render_template, Response, request, send_file
from camera_flask_setup import VideoCamera
import time
import threading
import os
import json
from gpiozero import Servo
import pigpio
import io
import cv2
import numpy as np


from maze_thread import MazeThread 
from image_utils import draw_grid, trim_maze_edge
from arUco import find_markers
from skew_correction import get_four_corners_from_two_opposites, four_point_transform
from colour_thresholding import locate_ball
from bfs import solve 
from image_test import maze_compression
from click_test import draw_path 

import servotest # instantiates pwm
from servotest import smooth_rotate
from servotest import MAX_ADJUSTED, MIN_ADJUSTED, SERVO_PIN_1


# Flask App
app = Flask(__name__, static_folder="static")

### Flask Routes ###
@app.route('/',methods=('GET','POST'))
def index():
    template_data = {
	'v_width':pi_camera.w//scale, 
	'p_width':crop_region[0]//scale, 
    'v_height':pi_camera.h//scale,
    'p_height':crop_region[1]//scale,
	'setting_blur':maze_thread.blur,
	'setting_thresh':maze_thread.block,
	'setting_sens':maze_thread.sensitivity*100
	}
    
    if request.method=='POST':
        blur = int(request.form['blur'])
        thresh = int(request.form['thresh'])
        sens = float(int(request.form['sens'])/100.0)
        maze_thread.blur = blur if blur%2 else blur+1 # must be odd
        maze_thread.block = thresh if thresh%2 else thresh+1
        maze_thread.sensitivity = sens
        template_data = { 
            **template_data,    # add default template data - and overwrite any new data
            'v_width':pi_camera.w, 
            'v_height':pi_camera.h,
            'setting_blur': blur,       
            'setting_thresh':thresh,
            'setting_sens': sens*100 
        }
    return render_template('index.html', **template_data)

def frame_gen():
    #get camera frame
    while True:
        frame = pi_camera.get_latest_frame() # TODO: make new frame feed for processed frames
        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

def processed_frame_gen():
    #get camera frame
    while True:
        frame = pi_camera.get_latest_processed_frame()

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

def maze_gen():
    #get maze frame
    path = None
    while True:
        frame = maze_thread.get_scaled_maze()
        if maze_thread.ball_position and maze_thread.target_cell:
            path = solve_maze()
            if path is not None:
                draw_path(frame, path, (maze_thread.x_grids*2+1, maze_thread.y_grids*2+1))

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')


def ref_gen():
    #get ref frame
    while True:
        frame = maze_thread.get_ref_image()

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(frame_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/processed_feed')
def processed_feed():
    return Response(processed_frame_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/maze_feed')
def maze_feed():
    return Response(maze_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/ref_feed')
def ref_feed():
    return Response(ref_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    print(f"Saving Picture")
    img = pi_camera.get_latest_processed_frame()
    # img = pi_camera.get_latest_frame()
    res, im_buf_arr = cv2.imencode(".jpg", img)
    bytes_img = io.BytesIO(im_buf_arr.tobytes())
    return send_file(bytes_img, as_attachment=True, download_name="pi_camera_capture.jpg")

@app.route('/calibrate')
def calibrate():
    maze_thread.update_maze()
    return json.dumps({"success": True}), 200

@app.route('/up')
def up():
    print("up")
    print("0 deg")
    smooth_rotate(SERVO_PIN_1, MAX_ADJUSTED)
    # pwm.set_servo_pulsewidth(SERVO_PIN_1,2000)
    return json.dumps({"success": True}), 200

@app.route('/down')
def down():
    print("down")
    print("90 deg")
    smooth_rotate(SERVO_PIN_1, MIN_ADJUSTED)
    # pwm.set_servo_pulsewidth(SERVO_PIN_1,500)
    return json.dumps({"success": True}), 200

@app.route('/left')
def left():
    print("left")
    print("90 deg")
    smooth_rotate(SERVO_PIN_1, MAX_ADJUSTED)
    # pwm.set_servo_pulsewidth(SERVO_PIN_2,500)    
    return json.dumps({"success": True}), 200

@app.route('/right')
def right():
    print("right")
    print("0 deg")
    smooth_rotate(SERVO_PIN_1, MIN_ADJUSTED)
    # pwm.set_servo_pulsewidth(SERVO_PIN_2,1000)
    return json.dumps({"success": True}), 200

@app.route('/grid_click', methods=['POST'])
def grid_click():
    cell_num = int(json.loads(request.get_data())['cell'])
    
    x = cell_num%(maze_thread.x_grids * 2 + 1)
    y = cell_num//(maze_thread.y_grids * 2 + 1)

    maze_thread.target_cell = (x,y)

    return json.dumps({"success": True}), 200

def solve_maze():
    maze = maze_thread.read_latest()
    for i in range(len(maze)): # switch 1s and 0s (convention)
        for j in range(len(maze[0])):
            maze[i][j] = int(not maze[i][j])
    return solve(maze, maze_thread.ball_position[::-1], maze_thread.target_cell[::-1])

if __name__ == '__main__':

    # Camera Setup
    mode = 0
    scale = 1
    resolution = (320*scale, 240*scale)
    crop_region = (min(resolution),)*2
    pi_camera = VideoCamera(
        resolution=resolution, 
        sensor_mode=mode, 
        correction=True, 
        crop_region=crop_region, 
        skew_fix=True
    ) # in a thread

    # start maze thread
    maze_thread = MazeThread(pi_camera) # in a thread

    # start flask server
    app.run(host='0.0.0.0', port=5000, threaded=True) #debug incompatible with resources available


