# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import os,time,json
from apscheduler.schedulers.background import BackgroundScheduler
import logging as log
from pi_sensor import DS18B20, Relay


class Aquarium:
    '''
    fish tank
    '''
    runmode = 0  #0-normal, 1-change water
    light_status = 0  #0-off, 1-on
    pump_status = 0  #0-off, 1-on
    pump_ext_status = 0 #0-off, 1-on
    heater_status = 0  #0-off, 1-on
    uv_status = 0  #0-off, 1-on
    temperature = 0  #temp get from sensor
    temp_heater_on = 24  #below this temp, heater on
    temp_heater_off = 27  #above this temp, heater off

    light_relay=None
    heater_relay=None
    uvlight_relay=None
    pump_relay=None
    pumpext_relay=None    
    temp_sensor = None
    scheduler = BackgroundScheduler()
    jobs = []

    def __init__(self):
        self.reload_cfg()
        self.set_runmode(0)
        self.get_temperature()

        job = self.scheduler.add_job(self.pump_ext_on, 'cron', hour='15')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.pump_ext_off, 'cron', hour='16')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.uv_on,
                                     'cron',
                                     #day_of_week='mon',
                                     hour='15')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.uv_off,
                                     'cron',
                                     #day_of_week='mon',
                                     hour='16',
                                     #minute='30')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.get_temperature,
                                     'interval',
                                     minutes=5)
        self.jobs.append(job)
        job = self.scheduler.add_job(self.light_on,
                                     'cron',
                                     hour='19')
        self.jobs.append(job)
        job = self.scheduler.add_job(self.light_off,
                                     'cron',
                                     hour='22')
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
            self.pump_on()
        if mode == 1:
            log.info("switch to changing water mode")
            for job in self.jobs:
                job.pause()
            self.uv_off()
            self.pump_ext_off()
            self.pump_off()
            self.light_off()
            self.heater_off()

    def get_runmode(self):
        return self.runmode

    def light_on(self):
        if self.light_relay is None:
            return
        self.light_relay.close()
        #pin = self.pins[0]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.HIGH)
        self.light_status = 1
        #log.info("light on")

    def light_off(self):
        if self.light_relay is None:
            return
        self.light_relay.open()
        #pin = self.pins[0]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.LOW)
        self.light_status = 0
        #log.info("light off")

    def pump_on(self):
        if self.pump_relay is None:
            return
        self.pump_relay.close()
        #pin = self.pins[1]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.HIGH)
        self.pump_status = 1
        #log.info("pump on")

    def pump_off(self):
        if self.pump_relay is None:
            return
        self.pump_relay.open()
        #pin = self.pins[1]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.LOW)
        self.pump_status = 0
        #log.info("pump off")

    def pump_ext_on(self):
        if self.pumpext_relay is None:
            return
        self.pumpext_relay.close()
        #pin = self.pins[2]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.HIGH)
        self.pump_ext_status = 1
        #log.info("external pump on")

    def pump_ext_off(self):
        if self.pumpext_relay is None:
            return
        self.pumpext_relay.open()
        #pin = self.pins[2]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.LOW)
        self.pump_ext_status = 0
        #log.info("external pump off")

    def uv_on(self):
        if self.uvlight_relay is None:
            return
        self.uvlight_relay.close()
        #pin = self.pins[3]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.HIGH)
        self.uv_status = 1
        #log.info("UV light on")

    def uv_off(self):
        if self.uvlight_relay is None:
            return
        self.uvlight_relay.open()
        #pin = self.pins[3]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.LOW)
        self.uv_status = 0
        #log.info("UV light off")

    def heater_on(self):
        if self.heater_relay is None:
            return
        self.heater_relay.close()
        #pin = self.pins[4]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.HIGH)
        self.heater_status = 1
        #log.info("heater on")

    def heater_off(self):
        if self.heater_relay is None:
            return
        self.heater_relay.open()
        #pin = self.pins[4]
        #if pin > 0:
        #    GPIO.output(pin, GPIO.HIGH)
        self.heater_status = 0
        #log.info("heater off")

    def get_temperature(self):
        if self.temp_sensor is None:
            return -30
        self.temperature = self.temp_sensor.get_temperature()
        temp = self.temperature 
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
        
    def set_temp_heater_on(self, temp):
        if temp<10:
            return
        self.temp_heater_on=temp
    def set_temp_heater_off(self, temp):
        if temp<self.temp_heater_on+2:
            log.error("Set Heater-off temperature %d failed, because the setting value should be higher than Heater-on temperature at least 2 degrees.",temp)
            return
        if temp>40:
            log.error("Set Heater-off temperature %d failed, because the setting value is too much high above 40 degrees",temp)
            return
        self.temp_heater_off=temp

    #s1-22, s2-18, s3-17, s4-27
    #s1-heater, s2-pump_ext, s3-uv s4-light
    def reload_cfg(self):
        fpath=os.path.dirname(os.path.abspath(__file__)) 
        cfg = dict()    
        with open(fpath+'/aquarium_cfg.json') as cfgfile:
            cfg = json.load(cfgfile)
        #print(cfg)
        # set light
        obj=cfg['light']
        if obj is not None:
            self.light_relay=Relay(obj['relay']['pin'],obj['relay']['reverse'])
            #print(obj['relay']['pin'])
            #print(obj['relay']['reverse'])
        # set heater
        obj=cfg['heater']
        if obj is not None:
            self.heater_relay=Relay(obj['relay']['pin'],obj['relay']['reverse'])
            temp=obj['heater_on_temp']
            if temp is not None and temp>10:
                self.temp_heater_on=temp
            temp=obj['heater_off_temp']
            if temp is not None and temp<40 and temp>self.temp_heater_on+1:
                self.temp_heater_off=temp              
            #print(self.temp_heater_on)
            #print(self.temp_heater_off)
        # set pump
        obj=cfg['pump']
        if obj is not None:
            self.pump_relay=Relay(obj['relay']['pin'],obj['relay']['reverse'])
        # set pumpext
        obj=cfg['pumpext']
        if obj is not None:
            self.pumpext_relay=Relay(obj['relay']['pin'],obj['relay']['reverse'])
        # set uvlight
        obj=cfg['uvlight']
        if obj is not None:
            self.uvlight_relay=Relay(obj['relay']['pin'],obj['relay']['reverse'])
        # set temp_sensor
        obj=cfg['temp_sensor']
        if obj is not None:
            self.temp_sensor=DS18B20(obj['serial'],obj['calib'])
        
    def get_status(self):
        st = {}
        st['runmode'] = (self.runmode==0) and 'Normal' or 'Change Water'
        st['light'] = (self.light_status==0) and 'Off' or 'On'
        st['heater'] = (self.heater_status==0) and 'Off' or 'On'
        st['uvlight'] = (self.uv_status==0) and 'Off' or 'On'
        st['pump'] = (self.pump_status==0) and 'Off' or 'On'
        st['pump_ext'] = (self.pump_ext_status==0) and 'Off' or 'On'
        st['temperature'] = round(self.temperature,2)
        st['temp_heater_on']=self.temp_heater_on
        st['temp_heater_off']=self.temp_heater_off
        return st

