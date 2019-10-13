#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import raspberrypi.pi_sensor as sensor


def test():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    dht = sensor.DHT11(18)
    hum, temp = dht.get_hum_temp()

    print("temperature :", temp, "*C, humidity:", hum, "%")
    GPIO.cleanup()


test()
