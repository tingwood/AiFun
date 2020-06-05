#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time
import logging
from pi_sensor import Tracker,HCSR04,Servo,InfraredObstacle
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
LOBT=13
ROBT=5
SERVO=26

RESET=0
STOP=10
FORWARD=11
BACKWARD=12
TURNLEFT=13
TURNRIGHT=14
TURN=15	# random turn

status = 0
distance = 0.
left_Obt = False
right_Obt = False
__sensor_running = True
__do_running = True

hcsr04 = HCSR04(TRIG, ECHO)
lTrk= Tracker(LTRK)
rTrk= Tracker(RTRK)
lObt= InfraredObstacle(LOBT)
rObt= InfraredObstacle(ROBT)
#servo=Servo(SERVO)
#servo1.angle(30)

GPIO.setup([ENA,ENB,IN1,IN2,IN3,IN4], GPIO.OUT ,initial=GPIO.LOW)
pwmA=GPIO.PWM(ENA,50)
pwmB=GPIO.PWM(ENB,50)
PWMA_DFAULT = 70	# 默认占空比
PWMB_DFAULT = 90


def __rotate(pin1, pin2, val):
	GPIO.output(pin1, val)
	GPIO.output(pin2, not(val))
	
def __right_forward(pwm):
	pwmA.ChangeDutyCycle(pwm)
	__rotate(IN1, IN2, True)

def __right_backward(pwm):
	pwmA.ChangeDutyCycle(pwm)
	__rotate(IN1, IN2, False)
	
def __left_forward(pwm):
	pwmB.ChangeDutyCycle(pwm)
	__rotate(IN3, IN4, False)
	
def __left_backward(pwm):
	pwmB.ChangeDutyCycle(pwm)
	__rotate(IN3, IN4, True)

def stop():
	global status
	status = STOP
	logging.info("Stop")
	GPIO.output([IN1,IN2,IN3,IN4], GPIO.LOW)

def reset():
	global status
	status = RESET
	GPIO.output([IN1,IN2,IN3,IN4], GPIO.LOW)
	
def forward():	
	global status
	status = FORWARD
	logging.info("Forward")
	__left_forward(PWMB_DFAULT)
	__right_forward(PWMA_DFAULT)
	
def backward():	
	global status
	status = BACKWARD
	logging.info("Backward")	
	__left_backward(PWMB_DFAULT)
	__right_backward(PWMA_DFAULT)


def turn_left():	
	global status
	status = TURNLEFT
	logging.info("Trun left")
	__left_backward(100)
	__right_forward(100)

def turn_right():
	global status
	status = TURNRIGHT
	logging.info("Trun right")
	__left_forward(100)
	__right_backward(100)


def do_cmd(cmd):
	global status
	if status == RESET:
		return
	if cmd == STOP:
		stop()
	elif cmd == FORWARD and status != FORWARD:
		forward()
	elif cmd == BACKWARD and status != BACKWARD:
		backward()
	elif cmd == TURNLEFT and status != TURNLEFT:
		turn_left()
	elif cmd == TURNRIGHT and status != TURNRIGHT:
		turn_right()
	elif cmd == TURN and status != TURNLEFT and status != TURNRIGHT:
		if random.random()<0.5:
			turn_right()
		else:
			turn_left()

def __sen_thread_func(interval):
	logging.info("sensor thread started")
	global distance
	global left_Obt
	global right_Obt
	distance = hcsr04.get_distance()	
	logging.info("Initial distance is %s cms" , distance)
	while(__sensor_running):
		temp = hcsr04.get_distance()
		if temp == -1: # measure failed
			continue
		#elif abs(temp - distance)/distance>25: # 
		#	continue			
		elif distance < 10 and temp > 2000: # too close, distance invalid
			temp=1		
		distance = temp	
		
		left_Obt = lObt.obstacle()	
		right_Obt = rObt.obstacle()
		time.sleep(interval)
		
	logging.info("sensor thread finished")


		
def __do_thread_func():
	global distance
	logging.info("Do command thread started")
	while(__do_running):
		if right_Obt:
			cmd = TURNLEFT
		elif left_Obt:
			cmd = TURNRIGHT
		elif distance<10:
			cmd = BACKWARD
		elif distance<30:
			# found obstacle event
			cmd = TURN
		elif distance>50:
			# no obstacle event
			cmd = FORWARD
		
		do_cmd(cmd)
		logging.debug("Do command is %s",cmd)
		time.sleep(0.1)
	logging.info("Do command thread finished")

def init(): 
    reset()
    # start sensor thread
    global __sensor_running
    __sensor_running = True
    sen_thread = threading.Thread(target=__sen_thread_func, args=[0.05])
    #sen_thread.setDaemon(True)
    sen_thread.start()
    logging.info("sensor thread started")
    
    # start do thread
    global __do_running
    __do_running = True
    do_thread = threading.Thread(target=__do_thread_func)
    #do_thread.setDaemon(True)
    do_thread.start()
    
    pwmA.start(PWMA_DFAULT)
    pwmB.start(PWMB_DFAULT)

def destroy():
	# stop do thread
	global __do_running
	__do_running = False	
	
	# stop sensor thread
	global __sensor_running
	__sensor_running = False
	
	reset()
	
	pwmA.stop()  
	pwmB.stop()

if __name__ == '__main__':
	logging.basicConfig(#filename='./car.log',\
                        #filemode='w',\
                        level=logging.INFO)
	init()
	with Board() as board:
		board.button.wait_for_press()
		if status == RESET:
			forward()	# start to forward
			board.led.state = Led.ON
		else:
			reset()
			board.led.state = Led.OFF
		board.button.wait_for_press()
		reset()
		board.led.state = Led.OFF
	destroy()
	exit(0)
