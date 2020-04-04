# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time
from apscheduler.schedulers.background import BackgroundScheduler
import logging as log
from pi_sensor import DS18B20


class Fishtank:
    '''
    fish tank
    '''
    runmode = 0  #0-normal, 1-change water
    light_status = 0  #0-off, 1-on
    pump_status = 0  #0-off, 1-on
    pump_ext_status = 0
    heater_status = 0  #0-off, 1-on
    uv_status = 0
    temperature = 0  #temp get from sensor
    temp_offset = 0  #temp sensor calibration
    temp_heater_on = 16  #below this temp, heater on
    temp_heater_off = 22  #above this temp, heater off

    pins = []
    scheduler = BackgroundScheduler()
    jobs = []
    temp_sensor = DS18B20('28-01191a61480c')

    def __init__(self, lightPin, pumpPin, pumbExtPin, uvPin, heaterPin):
        self.pins = [lightPin, pumpPin, pumbExtPin, uvPin, heaterPin]
        GPIO.setup(self.pins, GPIO.OUT)
        self.pump_on()

        job = self.scheduler.add_job(self.pump_ext_on_comb, 'cron', hour='10')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.pump_ext_off_comb, 'cron', hour='11')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.uv_on,
                                     'cron',
                                     day_of_week='sat',
                                     hour='10')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.uv_off,
                                     'cron',
                                     day_of_week='sat',
                                     hour='10',
                                     minute='30')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.get_temperature,
                                     'interval',
                                     minutes=5)
        self.jobs.append(job)
        self.scheduler.start()

    def set_runmode(self, mode):
        if mode < 0 or mode > 1:
            return
        self.runmode = mode
        if mode == 0:
            log.info("switch to auto-running mode")
            for job in self.jobs:
                job.resume()
        if mode == 1:
            log.info("switch to changing water mode")
            for job in self.jobs:
                job.pause()
            self.uv_off()
            self.pump_ext_off()
            self.pump_off()
            self.light_on()
            self.heater_on()

    def get_runmode(self):
        return self.runmode

    def light_on(self):
        pin = self.pins[0]
        if pin > 0:
            GPIO.output(pin, GPIO.HIGH)
        self.light_status = 1
        log.info("light on")

    def light_off(self):
        pin = self.pins[0]
        if pin > 0:
            GPIO.output(pin, GPIO.LOW)
        self.light_status = 1
        log.info("light off")

    def pump_on(self):
        pin = self.pins[1]
        if pin > 0:
            GPIO.output(pin, GPIO.HIGH)
        self.pump_status = 1
        log.info("pump on")

    def pump_off(self):
        pin = self.pins[1]
        if pin > 0:
            GPIO.output(pin, GPIO.LOW)
        self.pump_status = 0
        log.info("pump off")

    def pump_ext_on(self):
        pin = self.pins[2]
        if pin > 0:
            GPIO.output(pin, GPIO.HIGH)
        self.pump_ext_status = 1
        log.info("external pump on")

    def pump_ext_off(self):
        pin = self.pins[2]
        if pin > 0:
            GPIO.output(pin, GPIO.LOW)
        self.pump_ext_status = 0
        log.info("external pump off")

    def uv_on(self):
        pin = self.pins[3]
        if pin > 0:
            GPIO.output(pin, GPIO.HIGH)
        self.uv_status = 1
        log.info("UV light on")

    def uv_off(self):
        pin = self.pins[3]
        if pin > 0:
            GPIO.output(pin, GPIO.LOW)
        self.uv_status = 0
        log.info("UV light off")

    def heater_on(self):
        pin = self.pins[4]
        if pin > 0:
            GPIO.output(pin, GPIO.HIGH)
        self.heater_status = 1
        log.info("heater on")

    def heater_off(self):
        pin = self.pins[4]
        if pin > 0:
            GPIO.output(pin, GPIO.HIGH)
        self.heater_status = 0
        log.info("heater off")

    def get_temperature(self):
        self.temperature = self.temp_sensor.get_temperature()
        temp = self.temperature + self.temp_offset
        log.info("Current temperature is %d", temp)
        if temp < self.temp_heater_on and temp > 0:
            log.info("Current temperature is lower than %d",
                     self.temp_heater_on)
            self.heater_on()
        if temp > self.temp_heater_off:
            log.info("Current temperature is higher than %d",
                     self.temp_heater_off)
            self.heater_off()
        return temp

    def get_status(self):
        st = {}
        st['runmode'] = self.runmode
        st['light'] = self.light_status
        st['heater'] = self.heater_status
        st['uvlight'] = self.uv_status
        st['pump'] = self.pump_status
        st['pump_ext'] = self.pump_ext_status
        st['temprature'] = self.get_temperature()
        return st

    def pump_ext_on_comb(self):
        self.pump_ext_on()
        self.pump_off()

    def pump_ext_off_comb(self):
        self.pump_ext_off()
        self.pump_on()