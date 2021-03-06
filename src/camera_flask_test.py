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
import atexit

from maze_thread import MazeThread 
from image_utils import draw_grid, trim_maze_edge
from arUco import find_markers
from skew_correction import get_four_corners_from_two_opposites, four_point_transform
from colour_thresholding import locate_ball
from bfs import solve 
from image_test import maze_compression
from click_test import draw_path 
from click_test import servo_move

import servotest # instantiates pwm
from servotest import smooth_rotate, current_pwm, initilizePWM, releasePWM
from servotest import SERVO_PIN_1, SERVO_PIN_2, BIAS1, BIAS2, MAX_ADJUSTED, MIN_ADJUSTED


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

        # corners = pi_camera.avg_corner_pts
        # for c in corners:
        #     cv2.circle(frame, tuple(c), 5, (0,255,0), thickness=-1)

        # f = pi_camera.get_corner_mask()
        # cnts = cv2.findContours(f, cv2.RETR_TREE,
        #                 cv2.CHAIN_APPROX_SIMPLE)[1]
        # cnts = sorted(cnts, key=lambda cnt: cv2.contourArea(cnt), reverse=True)
    
        # for c in cnts[:4]:
        #     area = cv2.contourArea(c) 
        #     # print(area)
        #     # if area < 10: # likely not what we are looking for
        #     #     break
        # else:
        #     cnts =  [cv2.minEnclosingCircle(cnt) for cnt in cnts[:4]]
        #     for (x,y),r in cnts:
        #         frame = cv2.circle(frame, (int(x), int(y)), int(r), (0,0,255), thickness=2)
        #         frame[:,:,1] = frame[:,:,1]+f

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

@app.route('/start')
def start():
    global control_mode
    control_mode = 1
    return json.dumps({"success": True}), 200

@app.route('/stop')
def stop():
    global control_mode
    control_mode = 0
    return json.dumps({"success": True}), 200

@app.route('/calibrate')
def calibrate():
    maze_thread.update_maze()
    return json.dumps({"success": True}), 200

@app.route('/reset')
def reset():
    pi_camera.avg_corner_pts = [] # empty the avg points to allow corner detect to reset
    return json.dumps({"success": True}), 200

@app.route('/up')
def up():
    if control_mode == 0:
        global pwm1
        print("up")
        initilizePWM(SERVO_PIN_1, pwm1, BIAS1)
        pwm1 = smooth_rotate(SERVO_PIN_1, target=pwm1+50, bias=BIAS1)
        releasePWM(SERVO_PIN_1)
    return json.dumps({"success": True}), 200

@app.route('/down')
def down():
    if control_mode == 0:
        global pwm1
        print("down")
        initilizePWM(SERVO_PIN_1, pwm1, BIAS1)
        pwm1 = smooth_rotate(SERVO_PIN_1, target=pwm1-50, bias=BIAS1)
        releasePWM(SERVO_PIN_1)
    return json.dumps({"success": True}), 200

@app.route('/center')
def center():
    if control_mode == 0:
        global pwm1, pwm2
        print("center")

        initilizePWM(SERVO_PIN_1, pwm1, BIAS1)
        pwm1 = smooth_rotate(SERVO_PIN_1, target=(MAX_ADJUSTED+MIN_ADJUSTED)//2, bias=BIAS1)
        releasePWM(SERVO_PIN_1)

        initilizePWM(SERVO_PIN_2, pwm2, BIAS2)
        pwm2 = smooth_rotate(SERVO_PIN_2, target=(MAX_ADJUSTED+MIN_ADJUSTED)//2, bias=BIAS2)
        releasePWM(SERVO_PIN_2)

    return json.dumps({"success": True}), 200

@app.route('/left')
def left():
    if control_mode == 0:
        global pwm2
        print("left")
        initilizePWM(SERVO_PIN_2, pwm2, BIAS2)
        pwm2 = smooth_rotate(SERVO_PIN_2, target=pwm2-50, bias=BIAS2)
        releasePWM(SERVO_PIN_2)
    return json.dumps({"success": True}), 200

@app.route('/right')
def right():
    if control_mode == 0:
        global pwm2
        print("right")
        initilizePWM(SERVO_PIN_2, pwm2, BIAS2)
        pwm2 = smooth_rotate(SERVO_PIN_2, target=pwm2+50, bias=BIAS2)
        releasePWM(SERVO_PIN_2)
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
    
    for ob_coord in maze_thread.obstacles:
        cx,cy = ob_coord
        maze[cy][cx] = 1 # make obstacles seem like a wall

    path = solve(maze, maze_thread.ball_position[::-1], maze_thread.target_cell[::-1])

    # convert path into commands for servo movement
    if path is not None:
        commands = servo_move(path[::-1])[1::2]
        next_2 = commands[:2]
        merged_command = ()
        if len(next_2) == 2:
            merged_command = (
                next_2[0][0] if next_2[0][0] != 'none' else next_2[1][0],
                next_2[0][1] if next_2[0][1] != 'none' else next_2[1][1]
            )
        else:
            merged_command = next_2[0]

        # print(merged_command)
        # TODO: cleanup this into functions
        if control_mode == 1:
            global pwm1, pwm2
            if merged_command[0] == 'left':
                initilizePWM(SERVO_PIN_2, pwm2, BIAS2)
                pwm2 = smooth_rotate(SERVO_PIN_2, target=pwm2-50, bias=BIAS2)
                releasePWM(SERVO_PIN_2)

            elif merged_command[0] == 'right':
                initilizePWM(SERVO_PIN_2, pwm2, BIAS2)
                pwm2 = smooth_rotate(SERVO_PIN_2, target=pwm2+50, bias=BIAS2)
                releasePWM(SERVO_PIN_2)
            
            if merged_command[1] == 'up':
                initilizePWM(SERVO_PIN_1, pwm1, BIAS1)
                pwm1 = smooth_rotate(SERVO_PIN_1, target=pwm1+50, bias=BIAS1)
                releasePWM(SERVO_PIN_1)
                
            elif merged_command[1] == 'down':
                initilizePWM(SERVO_PIN_1, pwm1, BIAS1)
                pwm1 = smooth_rotate(SERVO_PIN_1, target=pwm1-50, bias=BIAS1)
                releasePWM(SERVO_PIN_1)
    
    return path

def servo_cleanup():
    initilizePWM(SERVO_PIN_1, pwm1, BIAS1)
    smooth_rotate(SERVO_PIN_1, target=(MAX_ADJUSTED+MIN_ADJUSTED)//2, bias=BIAS1)
    releasePWM(SERVO_PIN_1)

    initilizePWM(SERVO_PIN_2, pwm2, BIAS2)
    smooth_rotate(SERVO_PIN_2, target=(MAX_ADJUSTED+MIN_ADJUSTED)//2, bias=BIAS2)
    releasePWM(SERVO_PIN_2)

if __name__ == '__main__':

    # Camera Setup
    camera_mode = 0
    scale = 1
    resolution = (320*scale, 240*scale)
    crop_region = (min(resolution),)*2
    pi_camera = VideoCamera(
        resolution=resolution, 
        sensor_mode=camera_mode, 
        correction=True, 
        crop_region=crop_region, 
        skew_fix=True
    ) # in a thread

    # start maze thread
    maze_thread = MazeThread(pi_camera) # in a thread

    # initialize servos
    pwm1 = (MAX_ADJUSTED+MIN_ADJUSTED)//2
    pwm2 = (MAX_ADJUSTED+MIN_ADJUSTED)//2
    # initilizePWM(SERVO_PIN_1, pwm1, BIAS1)
    # initilizePWM(SERVO_PIN_2, pwm2, BIAS2)

    # ensure servo cleanup on app exit
    atexit.register(servo_cleanup)

    # control mode (0:manual, 1:auto)
    control_mode = 0

    # start flask server
    app.run(host='0.0.0.0', port=5000, threaded=True) #debug incompatible with resources available


