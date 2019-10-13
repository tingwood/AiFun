#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import raspberrypi.pi_sensor as sensor
from picamera import PiCamera, Color
import time


def watering():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    soil = sensor.SoilSensor(11)
    relay = sensor.Relay(8)
    if soil.iswet():
        return

    print("Soil is dry, start watering")
    relay.trigger()
    count = 20
    while count:
        time.sleep(1)
        if soil.iswet():
            break
        else:
            print("Still dry, keep on watering")
        count = count - 1
    print("Watering finished")
    relay.untrigger()
    GPIO.cleanup()



def take_pic():
    camera = PiCamera()
    # camera.rotatio=180
    # Default is the monitor's resolution
    # still image(max 2592*1944), video (max 1920*1080)
    # min resolution 64*64
    camera.resolution = (1920, 1080)

    # when set max resolution, framerate should be 15
    # camera.framerate = 15
    # camera.brightness=70
    # camera.contrast=20

    # valid size are 6-160, default 32
    camera.annotate_text_size = 30
    camera.annotate_background = Color('black')
    annotation = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    camera.annotate_text = annotation
    camera.start_preview()
    # camera.IMAGE-EFFECTS
    # camera.image_effect = 'gpen'
    # camera.AWB_MODES
    camera.awb_mode = 'auto'
    # camera.EXPOSURE_MODES
    camera.exposure_mode = 'auto'

    # sleep for at least 2 seconds, sensor auto set its light levels
    time.sleep(3)

    camera.capture('./image.jpg')
    camera.stop_preview()
