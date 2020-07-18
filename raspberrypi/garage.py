# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
import logging as log
from pi_sensor import Relay


class Garage:
    '''
    Garage
    '''
    _relays = {}

    # s1-22, s2-18, s3-17, s4-27
    # s1-heater, s2-pump_ext, s3-uv s4-light
    def reload_cfg(self):
        fpath = os.path.dirname(os.path.abspath(__file__))
        cfg = dict()
        with open(fpath+'/garage_cfg.json') as cfgfile:
            cfg = json.load(cfgfile)
        # print(cfg)

        # set relays
        obj = cfg['relays']
        if obj is not None:
            self._relays['light'] = Relay(
                obj['relay']['pin'], obj['relay']['reverse'])

        

    def get_status(self):
        st = {}
        # st['runmode'] = (self._runmode == 0) and 'Normal' or 'Change Water'
        # st['light'] = self.switchers_status('light')
        # st['heater'] = self.switchers_status('heater')
        # st['uvlight'] = self.switchers_status('uvlight')
        # st['pump'] = self.switchers_status('pump')
        # st['pump_ext'] = self.switchers_status('pumpext')
        # st['water_temp'] = self.water_temp
        # st['temp_heater_on'] = self.temp_heater_on
        # st['temp_heater_off'] = self.temp_heater_off
        return st
