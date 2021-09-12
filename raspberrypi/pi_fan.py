#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import json
from pi_sensor import LED_3461BS
import RPi.GPIO as GPIO
import time


# Return CPU temperature as a float
def getCPUtemperature():
    f = os.popen("cat /sys/class/thermal/thermal_zone0/temp")
    temp = int(f.readline().strip())/1000
    return round(temp, 1)


def fanCtrl(fan_pin,on_temp,off_temp):
    if(on_temp<off_temp):
        print("fan on temp must greater than off temp!")
        return

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fan_pin, GPIO.OUT)
    on = False
    state = 'on'
    temp = getCPUtemperature()
    if temp >= on_temp:
        GPIO.output(fan_pin, on)
    if temp < off_temp:
        GPIO.output(fan_pin, not(on))
        state = 'off'
    
    info = {}
    info['CPUtemp'] = temp
    info['Fan'] = state


def showStatus():
    '''
     1  a  f  2  3  b 
     e  d  dp c  g  4
    '''
    led = LED_3461BS(19, 11, 12, 20, 21, 13, 7, 16, 26, 6, 5, 8)
    led.show('On')
    time.sleep(3)
    led.off()

if __name__ == '__main__':
    info = fanCtrl(fan_pin=24, on_temp=55, off_temp=50)
    print(json.dumps(info))
