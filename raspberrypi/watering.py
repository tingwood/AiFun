#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
from picamera import PiCamera, Color
import sensor
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

soil = sensor.SoilSensor(11)
relay = sensor.Relay(8)
if soil.isdry():
    print("Soil is dry, start watering")
    relay.trigger()

while True:
    if soil.iswet():
        relay.untrigger()
        print("Watering finished")
        break
    else:
        print("Still dry, keep on watering")

GPIO.cleanup()


def capture():
    camera = PiCamera()
    camera.resolution = (1920, 1080)

    # valid size are 6-160, default 32
    camera.annotate_text_size = 30
    # camera.annotate_background=Color('black')
    camera.annotate_text = 'annotation'
    camera.start_preview()
    # camera.IMAGE-EFFECTS
    camera.image_effect = 'gpen'
    # camera.AWB_MODES
    camera.awb_mode = 'auto'
    # camera.EXPOSURE_MODES
    camera.exposure_mode = 'auto'

    # sleep for at least 2 seconds, sensor auto set its light levels
    time.sleep(3)

    camera.capture('./image.jpg')

    camera.stop_preview()