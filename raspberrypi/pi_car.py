#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time

pin1=4
pin2=17
pin3=27
pin4=22

pins=[pin1,pin2,pin3,pin4]
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) 
GPIO.setup(pins, GPIO.OUT)

def left_forward():
	GPIO.output(pins[0], GPIO.HIGH)
	GPIO.output(pins[1], GPIO.LOW)

def left_backward():
	GPIO.output(pins[1], GPIO.HIGH)
	GPIO.output(pins[0], GPIO.LOW)
	
def right_forward():
	GPIO.output(pins[3], GPIO.HIGH)
	GPIO.output(pins[2], GPIO.LOW)
	
def right_backward():
	GPIO.output(pins[2], GPIO.HIGH)
	GPIO.output(pins[3], GPIO.LOW)

def stop():
	var=GPIO.LOW
	GPIO.output(pins[0], var)
	GPIO.output(pins[1], var)
	GPIO.output(pins[2], var)
	GPIO.output(pins[3], var)
	
def forward():
	left_forward()
	right_forward()
	
def backward():
	left_backward()
	right_backward()

def turn_left():
	left_backward()
	right_forward()

def turn_right():
	left_forward()
	right_backward()
	
stop()
forward()
time.sleep(2)
backward()
time.sleep(2)
turn_left()
time.sleep(2)
turn_right()
time.sleep(2)
stop()
	
