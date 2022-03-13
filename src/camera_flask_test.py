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

from maze_thread import MazeThread 
from image_utils import draw_grid


SERVO_PIN_1 = 25
SERVO_PIN_2 = 24


# Flask App
app = Flask(__name__, static_folder="static")

### Flask Routes ###
@app.route('/',methods=('GET','POST'))
def index():
    template_data = {
	'v_width':pi_camera.w, 
    'v_height':pi_camera.h,
	'setting_blur':maze_thread.blur,
	'setting_thresh':maze_thread.threshold,
	'setting_sens':maze_thread.sensitivity*100
	}
    if request.method=='POST':
        blur = int(request.form['blur'])
        thresh = int(request.form['thresh'])
        sens = float(int(request.form['sens'])/100.0)
        print("Blur:",blur)
        print("Thresh:",thresh)
        print("Sens:",sens)
        maze_thread.blur = blur if blur%2 else blur+1 # must be odd
        maze_thread.threshold = thresh # TODO: add adaptive thresholding
        maze_thread.sensitivity = sens
        template_data = {
            'v_width':pi_camera.w, 
            'v_height':pi_camera.h,
            'setting_blur': blur,       
            'setting_thresh':thresh,
            'setting_sens': sens*100 }
    return render_template('index.html', **template_data)

def frame_gen():
    #get camera frame
    while True:
        frame = pi_camera.get_latest_frame()
        h,w = frame.shape[:2]

        # draw crop region with red outline - don't actually crop
        crop_region = (240, 240)
        crop_amount_w = w - crop_region[0] 
        crop_amount_h = h - crop_region[1]

        # set crop region for the maze
        maze_thread.crop_region = crop_region

        grid_size = (8,8) # x,y
        grid_y = grid_size[1]
        grid_x = grid_size[0]
        draw_grid(frame, grid_y, grid_x, x_offset=crop_amount_w//2, y_offset=crop_amount_h//2)

        cv2.rectangle(frame, (crop_amount_w//2+1, crop_amount_h//2+1), (w-crop_amount_w//2-1, h-crop_amount_h//2-1), (0,0,255), 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')


def maze_gen():
    #get maze frame
    while True:
        frame = maze_thread.get_scaled_maze()
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

@app.route('/maze_feed')
def maze_feed():
    return Response(maze_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/ref_feed')
def ref_feed():
    return Response(ref_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/print_hello')
def print_hello():
    print("Start")
    return json.dumps({"success": True}), 200

@app.route('/print_test')
def print_test():
    print("Stop")
    return json.dumps({"success": True}), 200

@app.route('/capture')
def capture():
    print(f"Saving Picture")
    img = pi_camera.get_latest_frame()
    res, im_buf_arr = cv2.imencode(".jpg", img)
    bytes_img = io.BytesIO(im_buf_arr.tobytes())
    return send_file(bytes_img, as_attachment=True, download_name="pi_camera_capture.jpg")


# @app.route('/up')
# def up():
#     print("up")
#     print("0 deg")
#     pwm.set_servo_pulsewidth(SERVO_PIN_1,2000)
#     return json.dumps({"success": True}), 200

# @app.route('/down')
# def down():
#     print("down")
#     print("90 deg")
#     pwm.set_servo_pulsewidth(SERVO_PIN_1,500)
#     return json.dumps({"success": True}), 200

# @app.route('/left')
# def left():
#     print("left")
#     print("90 deg")
#     pwm.set_servo_pulsewidth(SERVO_PIN_2,500)    
#     return json.dumps({"success": True}), 200

# @app.route('/right')
# def right():
#     print("right")
#     print("0 deg")
#     pwm.set_servo_pulsewidth(SERVO_PIN_2,1000)
#     return json.dumps({"success": True}), 200

if __name__ == '__main__':

    # pwm = pigpio.pi()
    # pwm.set_mode(SERVO_PIN_1,pigpio.OUTPUT)
    # pwm.set_PWM_frequency(SERVO_PIN_1,50)
    # pwm.set_mode(SERVO_PIN_2,pigpio.OUTPUT)
    # pwm.set_PWM_frequency(SERVO_PIN_2,50)

    # Camera Setup
    mode = 0
    resolution = (320, 240)
    pi_camera = VideoCamera(resolution, sensor_mode=mode, correction=True) # in a thread

    # start maze thread
    maze_thread = MazeThread(pi_camera) # in a thread

    # start flask server
    app.run(host='0.0.0.0', port=5000, threaded=True) #debug incompatible with resources available
