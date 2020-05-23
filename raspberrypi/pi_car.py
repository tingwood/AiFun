#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time
from pi_sensor import Tracker,HCSR04


TRIG=3
ECHO=2
ENA=8
ENB=27
IN1=9
IN2=10
IN3=11
IN4=22
LTRK=12
RTRK=24
SERVO=5


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) 

GPIO.setup([ENA,ENB,IN1,IN2,IN3,IN4], GPIO.OUT)
pwmA=GPIO.PWM(ENA,80)
pwmB=GPIO.PWM(ENB,80)
pwmA.start(30)	# 30%占空比
pwmB.start(30)

lTracker= Tracker(LTRK)
rTracker= Tracker(RTRK)
dist=HCSR04(TRIG, ECHO)

def left_forward():
	GPIO.output(IN1, GPIO.HIGH)
	GPIO.output(IN2, GPIO.LOW)

def left_backward():
	GPIO.output(IN2, GPIO.HIGH)
	GPIO.output(IN1, GPIO.LOW)
	
def right_forward():
	GPIO.output(IN3, GPIO.HIGH)
	GPIO.output(IN2, GPIO.LOW)
	
def right_backward():
	GPIO.output(IN2, GPIO.HIGH)
	GPIO.output(IN3, GPIO.LOW)

def stop():
	var=GPIO.LOW
	GPIO.output(IN1, var)
	GPIO.output(IN2, var)
	GPIO.output(IN3, var)
	GPIO.output(IN4, var)
	
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
	
