#!/usr/bin/env python

from flask import Flask, render_template, Response
from pistreaming import PiStreamer
from picamera import PiCamera
from time import sleep
from datetime import datetime

from pygtail import Pygtail

import logging, os
from io import StringIO


app = Flask(__name__)

app.config["SECRET_KEY"] = "SECRETKEYSECRETKEYSECRETKEYSECRETKEYSECRETKEY"
app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", False)
app.config["JSON_AS_ASCII"] = False
logging.basicConfig(level=logging.ERROR)


log_dir = '/home/pi/log/'
log_file = log_dir+datetime.now().isoformat().replace(':','')[:-7]+'.log'

handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)

log = logging.getLogger('camera')
log.setLevel(logging.INFO)
log.addHandler(handler)


WIDTH = 640
HEIGHT = 480
FRAMERATE = 24
VFLIP = False
HFLIP = False

camera = PiCamera()
camera.resolution = 'HD'
camera.framerate = FRAMERATE
camera.vflip = VFLIP # flips image rightside up, as needed
camera.hflip = HFLIP # flips image left-right, as needed
sleep(1) # camera warm-up time

streamer = PiStreamer((WIDTH,HEIGHT),camera.framerate) # TODO: impliment resize
camera.start_recording(streamer.output,'yuv',resize=streamer.resolution)


# logging.basicConfig(filename='/home/pi/pistreamingapp.log', level=logging.INFO,
#                     format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s :%(message)s')


@app.route('/')
def index():
    log.info("route => '/env' - hit!")
    return render_template('index.html')


@app.route('/log')
def show_log():
    def generate():
        for line in Pygtail(log_file, every_n=1):
            print(line)
            yield "data:" + str(line) + "\n\n"
            sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')


@app.route('/cmd/<cmd>')
def cmd(cmd=None):
    # TODO impliment camera controller
    if cmd=='capture':
        fname = f"/home/pi/Pictures/{datetime.now().isoformat().replace(':','')[:-7]}.jpeg"
        camera.capture(fname, use_video_port=True)
        log.info("Image captured")
    else:
        log.error("Command not recognized")
        return f"{cmd}: failure", 200, {'Content-Type': 'text/plain'}
    return f"{cmd}: success", 200, {'Content-Type': 'text/plain'}

if __name__=='__main__':
    app.run(host='0.0.0.0', threaded=True, debug=False)
    # NOTE: changing debug to true causes problems with picamera
    
