#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
from time import sleep
from importlib import import_module
import os
from flask import Flask, render_template, Response
from threading import Thread

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_pi  import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)
# Definition des pins
M1_En = 7
M1_In1 = 21
M1_In2 = 20

M2_En = 8
M2_In1 = 16
M2_In2 = 12
GPIO_TRIGGER =4
GPIO_ECHO =3

# Creation d'une liste des pins pour chaque moteur pour compacter la su>
Pins = [[M1_En, M1_In1, M1_In2], [M2_En, M2_In1, M2_In2]]


# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(M1_En, GPIO.OUT)
GPIO.setup(M1_In1, GPIO.OUT)
GPIO.setup(M1_In2, GPIO.OUT)

GPIO.setup(M2_En, GPIO.OUT)
GPIO.setup(M2_In1, GPIO.OUT)
GPIO.setup(M2_In2, GPIO.OUT)

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)

GPIO.setup(GPIO_ECHO, GPIO.IN)

# Define the speed
M1_Vitesse = GPIO.PWM(M1_En, 100)
M2_Vitesse = GPIO.PWM(M2_En, 100)
M1_Vitesse.start(100)
M2_Vitesse.start(100)

latest_distance = 0 

def calculate_distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    
    TimeElapsed = StopTime - StartTime

    # multiply with the sonic speed (34300 cm/s) and divide by 2
    global latest_distance
    latest_distance = (TimeElapsed * 34300) / 2
    time.sleep(1)
    return latest_distance
global old_level
old_level=4

def capture(distance):
    if distance < 10:
        level = 4
    elif distance < 18:
        level = 3
    elif distance < 25:
        level = 2
    elif distance < 33:
        level = 1
    else:
        level = 0
    return level

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/stream')
def stream():
    def generate_data():
        global old_level
        level=0
        while True:
            # Increment the data value
             data_value =calculate_distance()
             level=capture(data_value)
             print(level)
            # Send the updated value as an SSE event
             if level != old_level:
                 old_level=level
                 print(level)
             yield f"data: {old_level} \n\n"
    return Response(generate_data(), mimetype='text/event-stream')

def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/up_side')
def sens1() :
    GPIO.output(Pins[0][1], GPIO.HIGH)
    GPIO.output(Pins[0][2], GPIO.LOW)
    GPIO.output(Pins[1][1], GPIO.HIGH)
    GPIO.output(Pins[1][2], GPIO.LOW)
    print("tourne dans le sens 1.")
    return 'true'

@app.route('/down_side')
def sens2() :
    GPIO.output(Pins[0][1], GPIO.LOW)
    GPIO.output(Pins[0][2], GPIO.HIGH)
    print("tourne dans le sens 2.")
    GPIO.output(Pins[1][1], GPIO.LOW)
    GPIO.output(Pins[1][2], GPIO.HIGH)
    return 'true'
@app.route('/stop')
def arretComplet() :
    GPIO.output(Pins[0][1], GPIO.LOW)
    GPIO.output(Pins[0][2], GPIO.LOW)
    GPIO.output(Pins[1][1], GPIO.LOW)
    GPIO.output(Pins[1][2], GPIO.LOW)
    print("Moteurs arretes.")
    return 'true'
@app.route('/left_side')
def left():
    GPIO.output(Pins[0][1], GPIO.LOW)
    GPIO.output(Pins[0][2], GPIO.HIGH)
    GPIO.output(Pins[1][1], GPIO.HIGH)
    GPIO.output(Pins[1][2], GPIO.LOW)
    return 'true'
@app.route('/right_side')
def right():
    GPIO.output(Pins[0][1], GPIO.HIGH)
    GPIO.output(Pins[0][2], GPIO.LOW)
    GPIO.output(Pins[1][1], GPIO.LOW)
    GPIO.output(Pins[1][2], GPIO.HIGH)
    return 'true'


if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True,debug=True)

