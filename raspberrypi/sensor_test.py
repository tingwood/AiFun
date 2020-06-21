#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import sys
sys.path.append("..")
import RPi.GPIO as GPIO
import pi_sensor as sensor
import time
from utils import utils


def test_DHT111():
    data = []
    pin =23
    def cb(pin):
        print ("detect falling")
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
    time.sleep(0.03)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(2)
    GPIO.output(pin, GPIO.HIGH)   
         
    GPIO.setup(pin, GPIO.IN)    
    GPIO.add_event_detect(pin,GPIO.FALLING,callback=cb)
    time.sleep(1)
    

def test_DHT11():
    dht = sensor.DHT11(18)
    hum, temp,chk= dht.get_hum_temp()
    
    if chk:
        print("temperature :", temp, "*C, humidity:", hum, "%")
    else:
        print("check false")

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
    rgb=sensor.RGBLed(21,17,27)
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

def test_DS18B20():
    sen=sensor.DS18B20('28-01191a61480c')
    print (sen.get_temperature())

def test_Ultrasonic():
    sen=sensor.HCSR04(3,2)
    print(sen.get_distance())

def test_obstacle():
    sen=sensor.ObjDetector(13)
    print(sen.detected())

def test_3461BS():
    '''
     1  a  f  2  3  b 
     e  d  dp c  g  4
    '''
    sen=sensor.LED_3461BS(19,11,12,20,21,13,7,16,26,6,5,8)
    sen.show('efgh')
    time.sleep(5)
    sen.off()
    time.sleep(1)

def test_servo():
    servo=sensor.Servo(26)
    servo.angle(0)
    time.sleep(2)
    servo.angle(90)
    time.sleep(2)
    servo.angle(180)
    time.sleep(2)
   
    
def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    #test_DHT11()
    #test_RGB()
    #test_Tracker()
    #test_DS18B20()
    #test_Ultrasonic()
    #test_3461BS()
    #test_servo()
    test_obstacle()
    GPIO.cleanup()

main()
