from flask import Flask, render_template, Response, request
from camera_flask_setup import VideoCamera
import time
import threading
import os
import json

# Camera Setup
mode = 1
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
    data = {'v_width':pi_camera.w, 'v_height':pi_camera.h}
    return render_template('index.html', data=data) #you can customze index.html here

@app.route('/video_feed')
def video_feed():
    return Response(frame_gen(pi_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/print_hello')
def print_hello():
    print("Hello")
    return json.dumps({"success": True}), 200

@app.route('/print_test')
def print_test():
    print("Hello")
    return json.dumps({"success": True}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True) #debug incompatible with resources available