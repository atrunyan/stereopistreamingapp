import logging
from picamera import PiCamera
from datetime import datetime
from time import sleep
from pistreaming import PiStreamer

import RPi.GPIO as GPIO

LED_PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN,GPIO.OUT)
LIGHTS_STATUS = True
GPIO.output(LED_PIN,LIGHTS_STATUS)

CAMERA_PORT = 0
RECORDER_PORT = 1
STREAMING_PORT = 2

RECORDING = False

picam = PiCamera(camera_num=0, stereo_mode='none',
                 stereo_decimate=False, resolution=None,
                 framerate=None, sensor_mode=0,
                 led_pin=None, clock_mode='reset',
                 framerate_range=None)
sleep(2)                        # Let camera warm up

# TODO: add flip and rotate commands

log_dir = '/home/pi/log/'
LOG_FILE = log_dir+datetime.now().isoformat().replace(':','')[:-7]+'.log'

handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)

log = logging.getLogger('camera')
log.setLevel(logging.INFO)
log.addHandler(handler)


def now():
    return datetime.now().isoformat().replace(':','')[:-7]    

def capture():
    output = f'/home/pi/Pictures/{now()}.jpg'
    # NOTE: use video port to speed up capture
    picam.capture(output, use_video_port=True, resize=None,
                  splitter_port=CAMERA_PORT, bayer=False)
    log.info("Image captured")

def start_recording():
    global RECORDING
    if RECORDING:
        stop_recording()
    output = f'/home/pi/Videos/{now()}.h264'
    picam.start_recording(output, resize=None,
                          splitter_port=RECORDER_PORT)
    RECORDING = True
    log.info("Recording started")

def stop_recording():
    global RECORDING
    if not RECORDING:
        log.debug("No recording in progress")
        return
    picam.stop_recording(splitter_port=RECORDER_PORT)
    RECORDING = False
    log.info("Recording ended")

def start_streaming(resolution=(640,480)):
    streamer = PiStreamer(resolution,picam.framerate)
    picam.start_recording(streamer.output,'yuv',resize=streamer.resolution,
                          splitter_port=STREAMING_PORT)
    log.info("Websocket stream started")

def stop_streaming():
    picam.stop_recording(splitter_port=STREAMING_PORT)
    log.info("Websocket stream ended")


def toggle_lights(led_pin=4):
    global LIGHTS_STATUS
    LIGHTS_STATUS = not LIGHTS_STATUS
    GPIO.output(LED_PIN,LIGHTS_STATUS)
    log.info(f"Lights toggled to {LIGHTS_STATUS}")

        
