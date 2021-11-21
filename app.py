#!/usr/bin/env python

from flask import Flask, render_template, Response
from pistreaming import PiStreamer
from picamera import PiCamera
from time import sleep

WIDTH = 640
HEIGHT = 480
FRAMERATE = 24
VFLIP = False
HFLIP = False

camera = PiCamera()
camera.resolution = (WIDTH, HEIGHT)
camera.framerate = FRAMERATE
camera.vflip = VFLIP # flips image rightside up, as needed
camera.hflip = HFLIP # flips image left-right, as needed
sleep(1) # camera warm-up time

camera.close()

app = Flask(__name__)

@app.route('/')
def index():
    if camera.closed:
        camera.__init__()
        camera.resolution = (WIDTH, HEIGHT)
        camera.framerate = FRAMERATE
        camera.vflip = VFLIP # flips image rightside up, as needed
        camera.hflip = HFLIP # flips image left-right, as needed
        sleep(1) # camera warm-up time
        streamer = PiStreamer(camera)
        streamer.start()
    return render_template('index.html')


if __name__=='__main__':
    app.run(host='0.0.0.0', threaded=True,debug=False,port=1234)
    
