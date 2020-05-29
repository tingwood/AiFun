#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time
import logging as log
from pi_sensor import Tracker,HCSR04,Servo
import threading
from aiy.board import Board,Led
import random

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

TRIG=3
ECHO=2
ENA=8
IN1=9
IN2=10
IN3=11
IN4=22
ENB=7
LTRK=12
RTRK=24
SERVO=26

START=0
STOP=10
FORWARD=11
BACKWARD=12
TURNLEFT=13
TURNRIGHT=14
TURN=15	# random turn

status = 0
command = 0
__sensor_running = False
__do_running = False

hcsr04 = HCSR04(TRIG, ECHO)
lTrk= Tracker(LTRK)
rTrk= Tracker(RTRK)
servo=Servo(SERVO)
#servo1.angle(30)

GPIO.setup([ENA,ENB,IN1,IN2,IN3,IN4], GPIO.OUT ,inital=GPIO.LOW)
pwmA=GPIO.PWM(ENA,100)
pwmB=GPIO.PWM(ENB,100)
PWMA_DFAULT = 70	# 默认占空比
PWMB_DFAULT = 90
pwmA.start(PWMA_DFAULT)    
pwmB.start(PWMB_DFAULT)

def __rotate(pin1, pin2, val):
	GPIO.output(pin1, val)
	GPIO.output(pin1, not(val))
	
def __right_forward(pwm):
	pwmA.ChangeDutyCycle(pwm)
	__rotate(IN1, IN2, GPIO.HIGH)

def __right_backward(pwm):
	pwmA.ChangeDutyCycle(pwm)
	__rotate(IN1, IN2, GPIO.LOW)
	
def __left_forward(pwm):
	pwmB.ChangeDutyCycle(pwm)
	__rotate(IN3, IN4, GPIO.LOW)
	
def __left_backward(pwm):
	pwmB.ChangeDutyCycle(pwm)
	__rotate(IN3, IN4, GPIO.HIGH)

def stop():
	status = STOP
	log.info("Stop")
	GPIO.output([IN1,IN2,IN3,IN4], GPIO.LOW)

def start():
	status = START
	GPIO.output([IN1,IN2,IN3,IN4], GPIO.LOW)
	
def forward(interval):	
	status = FORWARD
	log.info("Forward")
	__left_forward(PWMB_DFAULT)
	__right_forward(PWMA_DFAULT)
	if interval>0:
		time.sleep(interval)
	
def backward(interval):	
	status = BACKWARD
	log.info("Backward")	
	__left_backward(PWMB_DFAULT)
	__right_backward(PWMA_DFAULT)
	if interval>0:
		time.sleep(interval)

def turn_left(interval):	
	status = TURNLEFT
	log.info("Trun left")
	__left_backward(100)
	__right_forward(100)
	if interval>0:
		time.sleep(interval)

def turn_right(interval):
	status = TURNRIGHT
	log.info("Trun right")
	__left_forward(100)
	__right_backward(100)
	if interval>0:
		time.sleep(interval)


def do_cmd(cmd):
	interval = 0.1
	if status == START:
		return
	if cmd == STOP:
		stop()
	elif cmd == FORWARD and status != FORWARD:
		forward(interval)
	elif cmd == BACKWARD and status != BACKWARD:
		backward(interval)
	elif cmd == TURNLEFT and status != TURNLEFT:
		turn_left(interval)
	elif cmd == TURNRIGHT and status != TURNRIGHT:
		turn_right(interval)
	elif cmd == TURN and status != TURNLEFT and status != TURNRIGHT:
		if random.random()<0.5:
			turn_right(interval)
		else:
			turn_left(interval)

def __sen_thread_func(interval):
	dist = hcsr04.get_distance()
	while(__sensor_running):
		temp = hcsr04.get_distance()
		if abs(temp - dist)/dist<25:
			dist = temp
		if dist<15:
			command = BACKWARD
		elif dist<50:
			# found obstacle event
			command = TURN
		elif dist>80:
			# no obstacle event
			command = FORWARD
		time.sleep(interval)
		
def __do_thread_func():
	while(__move_running):
		do_cmd(command)

def __init(): 
    start()
    # start sensor thread
    __sensor_running = True
    sen_thread = threading.Thread(target=__sen_thread_func, args=0.01)
    #sen_thread.setDaemon(True)
    sen_thread.start()
    
    # start do thread
    __do_running = True
    do_thread = threading.Thread(target=__do_thread_func)
    do_thread.start()

def destroy():
	# stop do thread
	__do_running = False	
	
	# stop sensor thread
	__sensor_running = False
	
	start()

if __name__ == '__main__':
	log.basicConfig(level=log.INFO)
	__init()
	with Board() as board:
		board.button.wait_for_press()
		if status == START:
			forward()	# start to forward
			board.led.state = Led.ON
		else:
			start()
			board.led.state = Led.OFF
		board.button.wait_for_press()
		start()
		board.led.state = Led.OFF
	destroy()
	exit(0)
