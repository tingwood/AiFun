#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import raspberrypi.pi_sensor as sensor
import time


def test_DHT11():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    dht = sensor.DHT111(7)
    hum, temp,chk= dht.get_hum_temp()

    print("temperature :", temp, "*C, humidity:", hum, "%")
    GPIO.cleanup()

def test_relay():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    relay = sensor.Relay(18)
    relay.trigger()
    time.sleep(2)
    relay.untrigger()
    time.sleep(2)
    GPIO.cleanup()

def test_RGB():
    rgb=sensor.RGBLed(4,17,27)
    rgb.red_blink(0.8,0.2)
    time.sleep(10)
    rgb.green_blink()
    time.sleep(10)
    rgb.blue_blink()
    time.sleep(10)   
    rgb.off()

def test_Tracker():
    sen=sensor.Tracker(4)
    while True:
        print(sen.reflect())
        time.sleep(1)

def test_Ultrasonic():
    sen=sensor.Ultrasonic(27,17)
    print(sen.distance())
    
def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    #test_RGB()
    #test_Tracker()
    test_Ultrasonic()
    GPIO.cleanup()

main()
