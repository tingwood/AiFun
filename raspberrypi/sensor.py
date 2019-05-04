#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time


class Sensor:
    '''
    Sensor base class
    '''
    pins = []  # sensor connected pins with raspberry pi

    def __init__(self, pins):
        self.pins = pins


class SoilSensor(Sensor):
    '''
    Soil humidity sensor
    dry: output GPIO.HIGH
    wet: output GPIO.LOW (DO-LED will light)
    '''
    sample = 20  # sample times
    dry_th = 0  # dry threshold
    wet_th = 0  # wet threshold

    def __init__(self, pin, sample=20):
        pins = [pin]
        super(SoilSensor, self).__init__(pins)
        if sample > 0:
            self.sample = sample
        self.dry_th = sample * 0.8
        self.wet_th = sample * 0.2
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def isdry(self):
        val = 0
        for i in range(0, self.sample):
            val += GPIO.input(self.pins[0])
            time.sleep(0.2)

        if val >= self.dry_th:  # dry
            return True
        else:
            return False

    def iswet(self):
        val = 0
        for i in range(0, self.sample):
            val += GPIO.input(self.pins[0])
            time.sleep(0.2)

        if val <= self.wet_th:  # wet
            return True
        else:
            return False


class Relay(Sensor):
    '''
    Relay:
    Connection with Raspi:
    VCC(DC+)：5V, pin2 or pin4
    GND(DC-)：GND, pin 6
    IN：GPIO, pin11 GPIO.LOW or GPIO.HIGH

    Output Control：
    NO： diconnect in usual, connect when trigger
    COM：common
    NC： connect in usual, disconnect when trigger

    Trigger jumpper：
    A jumpper can be set using GPIO.LOW or GPIO.HIGH to relay trigger
    '''

    def __init__(self, pin):
        pins = [pin]
        super(Relay, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)

    def trigger(self):
        GPIO.output(self.pins[0], GPIO.HIGH)

    def untrigger(self):
        GPIO.output(self.pins[0], GPIO.LOW)
