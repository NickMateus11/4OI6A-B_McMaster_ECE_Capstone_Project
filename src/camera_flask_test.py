from flask import Flask, render_template, Response, request, send_file
from camera_flask_setup import VideoCamera
import time
import threading
import os
import json
from gpiozero import Servo
import pigpio
import cv2


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

def frame_gen(camera):
    #get camera frame
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

### Flask Routes ###

@app.route('/')
def index():
    data = {
        'v_width':pi_camera.w, 
        'v_height':pi_camera.h
        }
    return render_template('index.html', **data) #you can customze index.html here

@app.route('/video_feed')
def video_feed():
    return Response(frame_gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/print_hello')
def print_hello():
    print("Start")
    return json.dumps({"success": True}), 200

@app.route('/print_test')
def print_test():
    print("Stop")
    return json.dumps({"success": True}), 200

captures = 0
@app.route('/capture')
def capture():
    global captures
    filename = f"pic_{captures}.png"
    # captures+=1
    print(f"Saving Picture {filename}")
    cv2.imwrite(filename, pi_camera.vs.read())
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
    app.run(host='0.0.0.0', port=5000, threaded=True) #debug incompatible with resources available
