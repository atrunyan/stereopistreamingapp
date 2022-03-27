#!/usr/bin/env python

from flask import Flask, render_template, Response
from time import sleep
from datetime import datetime
import camera

from pygtail import Pygtail

import logging, os
from io import StringIO

camera.start_streaming()


# Set up app
app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRETKEYSECRETKEYSECRETKEYSECRETKEYSECRETKEY"
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", False)
app.config["JSON_AS_ASCII"] = False
logging.basicConfig(level=logging.WARNING)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/log')
def show_log():
    def generate():
        for line in Pygtail(camera.LOG_FILE, every_n=1):
            print(line)
            yield "data:" + str(line) + "\n\n"
            sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')


@app.route('/cmd/capture')
def capture():
    logging.debug("Attempt to capture")
    camera.capture()
    return("nothing")

@app.route('/cmd/startrecord')
def start_recording():
    camera.start_recording()
    return("nothing")

@app.route('/cmd/stoprecord')
def stop_recording():
    camera.stop_recording()
    return("nothing")

@app.route('/cmd/lights')
def toggle_light():
    logging.debug("lights")
    camera.toggle_lights()
    return("nothing")

if __name__=='__main__':
    app.run(host='0.0.0.0', threaded=True, debug=False)
    # NOTE: changing debug to true causes problems with picamera
    
