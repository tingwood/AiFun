# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
import logging as log
from pi_sensor import DS18B20, Relay


class Aquarium:
    '''
    fish tank
    '''
    water_temp = 0  # temp get from sensor
    temp_heater_on = 25  # below this temp, heater on
    temp_heater_off = 27  # above this temp, heater off

    _runmode = 0  # 0-normal, 1-change water
    _temp_sensor = None
    _scheduler = None
    _jobs = []
    _relays = {}

    def __init__(self):
        self.reload_cfg()
        self.set_runmode(0)
        self.get_water_temp()

        self._scheduler = BackgroundScheduler()
        job = self._scheduler.add_job(self.pump_ext_on, 'cron', hour='15')
        self._jobs.append(job)
        job = self._scheduler.add_job(self.pump_ext_off, 'cron', hour='16')
        self._jobs.append(job)
        job = self._scheduler.add_job(self.uv_on,
                                      'cron',
                                      # day_of_week='mon',
                                      hour='15')
        self._jobs.append(job)
        job = self._scheduler.add_job(self.uv_off,
                                      'cron',
                                      # day_of_week='mon',
                                      hour='16',
                                      # minute='30'
                                      )
        self._jobs.append(job)
        job = self._scheduler.add_job(self.get_water_temp,
                                      'interval',
                                      minutes=5)
        self._jobs.append(job)
        job = self._scheduler.add_job(self.light_on,
                                      'cron',
                                      hour='19')
        self._jobs.append(job)
        job = self._scheduler.add_job(self.light_off,
                                      'cron',
                                      hour='22')
        self._jobs.append(job)
        self._scheduler.start()

    def __del__(self):
        if self._scheduler is None:
            return
        self._scheduler.shutdown()

    def set_runmode(self, mode):
        if mode == 0:
            log.info("switch to auto-running mode")
            for job in self._jobs:
                job.resume()
            self.pump_on()
        elif mode == 1:
            log.info("switch to changing water mode")
            for job in self._jobs:
                job.pause()
            self.uv_off()
            self.pump_ext_off()
            self.pump_off()
            self.light_off()
            self.heater_off()
        else:
            # raise exception
            return
        self._runmode = mode

    def get_runmode(self):
        return self._runmode

    def switchers_status(self, name):
        relay = self._relays[name]
        if relay is None:
            return 'unknown'
        if relay.isClose:
            return 'On'
        else:
            return 'Off'

    def switchers_on(self, name):
        relay = self._relays[name]
        if relay is None:
            #raise exception
            return
        relay.close()


    def switchers_off(self, name):
        relay = self._relays[name]
        if relay is None:
            #raise exception
            return
        relay.open()

    def light_on(self):
        self.switchers_on('light')
        self.light_status = 1
        # log.info("light on")

    def light_off(self):
        self.switchers_off('light')  
        self.light_status = 0
        # log.info("light off")

    def pump_on(self):
        self.switchers_on('pump')    
        self.pump_status = 1
        # log.info("pump on")

    def pump_off(self):
        self.switchers_off('pump')       
        self.pump_status = 0
        # log.info("pump off")

    def pump_ext_on(self):
        self.switchers_on('pumpext')
        self.pump_ext_status = 1
        # log.info("external pump on")

    def pump_ext_off(self):
        self.switchers_off('pumpext')
        self.pump_ext_status = 0
        # log.info("external pump off")

    def uv_on(self):
        self.switchers_on('uvlight')
        self.uv_status = 1
        # log.info("UV light on")

    def uv_off(self):
        self.switchers_off('uvlight')
        self.uv_status = 0
        # log.info("UV light off")

    def heater_on(self):
        self.switchers_on('heater')
        self.heater_status = 1
        # log.info("heater on")

    def heater_off(self):
        self.switchers_off('heater')
        self.heater_status = 0
        # log.info("heater off")

    def get_water_temp(self):
        if self._temp_sensor is None:
            return -100
        self.water_temp = round(self._temp_sensor.get_temperature(), 2)
        temp = self.water_temp
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

    # s1-22, s2-18, s3-17, s4-27
    # s1-heater, s2-pump_ext, s3-uv s4-light
    def reload_cfg(self):
        fpath = os.path.dirname(os.path.abspath(__file__))
        cfg = dict()
        with open(fpath+'/aquarium_cfg.json') as cfgfile:
            cfg = json.load(cfgfile)
        # print(cfg)

        # set light
        obj = cfg['light']
        if obj is not None:
            self._relays['light'] = Relay(
                obj['relay']['pin'], obj['relay']['reverse'])
            # print(obj['relay']['pin'])
            # print(obj['relay']['reverse'])

        # set heater
        obj = cfg['heater']
        if obj is not None:
            self._relays['heater'] = Relay(
                obj['relay']['pin'], obj['relay']['reverse'])
            temp = obj['heater_on_temp']
            if temp is not None and temp > 20:
                self.temp_heater_on = temp
            temp = obj['heater_off_temp']
            if temp is not None and temp < 40 and temp > self.temp_heater_on+1:
                self.temp_heater_off = temp
            # print(self.temp_heater_on)
            # print(self.temp_heater_off)

        # set pump
        obj = cfg['pump']
        if obj is not None:
            self._relays['pump'] = Relay(
                obj['relay']['pin'], obj['relay']['reverse'])

        # set pumpext
        obj = cfg['pumpext']
        if obj is not None:
            self._relays['pumpext'] = Relay(
                obj['relay']['pin'], obj['relay']['reverse'])

        # set uvlight
        obj = cfg['uvlight']
        if obj is not None:
            self._relays['uvlight'] = Relay(
                obj['relay']['pin'], obj['relay']['reverse'])

        # set _temp_sensor
        obj = cfg['temp_sensor']
        if obj is not None:
            self._temp_sensor = DS18B20(obj['serial'], obj['calib'])

    def get_status(self):
        st = {}
        st['runmode'] = (self._runmode == 0) and 'Normal' or 'Change Water'
        st['light'] = self.switchers_status('light')
        st['heater'] = self.switchers_status('heater')
        st['uvlight'] = self.switchers_status('uvlight')
        st['pump'] = self.switchers_status('pump')
        st['pump_ext'] = self.switchers_status('pumpext')
        st['water_temp'] = self.water_temp
        st['temp_heater_on'] = self.temp_heater_on
        st['temp_heater_off'] = self.temp_heater_off
        return st
