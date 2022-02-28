from flask import Flask, render_template, Response, request, send_file
from camera_flask_setup import VideoCamera
import time
import threading
import os
import json
from gpiozero import Servo
import pigpio
import cv2

from maze_thread import MazeThread 


SERVO_PIN_1 = 25
SERVO_PIN_2 = 24

# pwm = pigpio.pi()

# pwm.set_mode(SERVO_PIN_1,pigpio.OUTPUT)
# pwm.set_PWM_frequency(SERVO_PIN_1,50)

# pwm.set_mode(SERVO_PIN_2,pigpio.OUTPUT)
# pwm.set_PWM_frequency(SERVO_PIN_2,50)

# Camera Setup
mode = 0
resolution = (320, 240)
pi_camera = VideoCamera(resolution, sensor_mode=mode)

# Flask App
app = Flask(__name__, static_folder="static")

def frame_gen(feed, kwargs={}):
    #get camera frame
    while True:
        frame = feed.get_frame(**kwargs)
        _, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

### Flask Routes ###

@app.route('/')
def index():
    data = {
        'v_width':min(pi_camera.h, pi_camera.w), 
        'v_height':min(pi_camera.h, pi_camera.w)
        }
    return render_template('index.html', **data) #you can customze index.html here

@app.route('/video_feed')
def video_feed():
    kwargs = {"fisheye_correction": True, "crop_dim":(240, 240)}
    return Response(frame_gen(pi_camera, kwargs),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/maze_feed')
def maze_feed():
    return Response(frame_gen(maze_thread),
                mimetype='multipart/x-mixed-replace; boundary=frame')

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
    filename = "pic_temp.png"
    print(f"Saving Picture {filename}")
    kwargs = {"fisheye_correction": True, "crop_dim":(240, 240)}
    img = pi_camera.get_frame(**kwargs)
    cv2.imwrite(filename, img)
    return send_file(filename, as_attachment=True)

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

    # start maze thread
    maze_thread = MazeThread(pi_camera)
    maze_thread.start()

    # start flask server
    app.run(host='0.0.0.0', port=5000, threaded=True) #debug incompatible with resources available
