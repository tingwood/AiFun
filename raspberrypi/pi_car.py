#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time
import logging as log
from pi_sensor import Tracker,HCSR04,Servo
import threading
from aiy.board import Board,Led
import random

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
SERVO1=5

INIT=0
RUNNING=1
STOP=10
FORWARD=11
BACKWARD=12
TURNLEFT=13
TURNRIGHT=14
TURN=15

status=INIT

def right_forward():
	GPIO.output(IN1, GPIO.HIGH)
	GPIO.output(IN2, GPIO.LOW)

def right_backward():
	GPIO.output(IN2, GPIO.HIGH)
	GPIO.output(IN1, GPIO.LOW)
	
def left_forward():
	GPIO.output(IN4, GPIO.HIGH)
	GPIO.output(IN3, GPIO.LOW)
	
def left_backward():
	GPIO.output(IN3, GPIO.HIGH)
	GPIO.output(IN4, GPIO.LOW)

def stop():
	status = STOP
	var=GPIO.LOW
	GPIO.output(IN1, var)
	GPIO.output(IN2, var)
	GPIO.output(IN3, var)
	GPIO.output(IN4, var)
	
def forward():
	log.info("Forward")
	status = FORWARD
	pwmA.ChangeDutyCycle(pwmA_dft)
	pwmB.ChangeDutyCycle(pwmB_dft)
	left_forward()
	right_forward()
	time.sleep(0.1)
	
def backward():
	log.info("Backward")
	status = BACKWARD
	pwmA.ChangeDutyCycle(pwmA_dft)
	pwmB.ChangeDutyCycle(pwmB_dft)
	left_backward()
	right_backward()
	time.sleep(0.1)

def turn_left():
	log.info("Trun left")
	status = TURNLEFT
	pwmA.ChangeDutyCycle(100)
	pwmB.ChangeDutyCycle(100)
	left_backward()
	right_forward()
	time.sleep(0.1)

def turn_right():
	log.info("Trun right")
	status = TURNRIGHT
	pwmA.ChangeDutyCycle(100)
	pwmB.ChangeDutyCycle(100)
	left_forward()
	right_backward()
	time.sleep(0.1)

def is_turn(st):
	if st == TURNLEFT or st == TURNRIGHT:
		return True
	return False

def action(command):
	if status == INIT:
		return
	if command == STOP:
		stop()
	elif command == FORWARD and status != FORWARD:
		forward()
	elif command == BACKWARD and status != BACKWARD:
		backward()
	elif command == TURNLEFT and status != TURNLEFT:
		turn_left()
	elif command == TURNRIGHT and status != TURNRIGHT:
		turn_right()
	elif command == TURN and not(is_turn(status)):
		if random.random()<0.5:
			turn_right()
		else:
			turn_left()

def thread_func():
	dist = hcsr04.get_distance()
	while(__sensor_running):
		temp = hcsr04.get_distance()
		if abs(temp - dist)/dist<25:
			dist = temp
		if dist<15:
			action(BACKWARD)
		elif dist<50:
			# found obstacle event
			action(TURN)
		elif dist>80:
			# no obstacle event
			action(FORWARD)
		time.sleep(0.01)
def thread_func1(interval):
	while(__move_running):
		if command == STOP:
			stop()
		elif command == FORWARD:
			forward()
		elif command == BACKWARD:
			backward()
		elif command == TURNLEFT:
			turn_left()
		elif command == TURNRIGHT:
			turn_right()
		time.sleep(1)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) 

GPIO.setup([ENA,ENB,IN1,IN2,IN3,IN4], GPIO.OUT)
pwmA=GPIO.PWM(ENA,100)
pwmB=GPIO.PWM(ENB,100)
pwmA_dft=70
pwmB_dft=90
pwmA.start(pwmA_dft)    # 50%占空比
pwmB.start(pwmB_dft)

action(STOP)
status = INIT
__sensor_running = False
__move_running = False
hcsr04 = HCSR04(TRIG, ECHO)
action(STOP)

def init():
        lTracker= Tracker(LTRK)
        rTracker= Tracker(RTRK)

        servo1=Servo(SERVO1)
        #servo1.angle(30)
        #time.sleep(3)


if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    init()
    action(STOP)
    status = INIT
    # start sensor thread
    __sensor_running = True
    t1=threading.Thread(target=thread_func)
    #t1.setDaemon(True)
    t1.start()
    #print(t1.name)

    # start move thread
    #__move_running = True
    #t2=threading.Thread(target=thread_func1)
    #t2.start()
    with Board() as board:
        board.button.wait_for_press()
        if status == INIT:
            status = RUNNING
            board.led.state = Led.ON
        else:
            status = INIT
            board.led.state = Led.OFF
        action(FORWARD)
        board.button.wait_for_press()
        board.led.state = Led.OFF
    action(STOP)
    status=INIT
    log.debug("exit")
    __sensor_running = False
    #__move_running = False
    t1.join()
    
    #t2.join()
    GPIO.cleanup()
    exit(0)
	
#stop()
#forward()
#time.sleep(2)
#backward()
#time.sleep(2)
#turn_left()
#time.sleep(2)
#turn_right()
#time.sleep(2)
#stop()
	
