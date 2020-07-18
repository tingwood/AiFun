#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
from flask import Flask, request, jsonify
import json
import logging
import RPi.GPIO as GPIO
from aquarium import Aquarium
import pi_info

# o_path=os.getcwd()
fpath = os.path.dirname(os.path.abspath(__file__))  # pi_service dir
sys.path.append(fpath+"/../")
from utils import utils

logpath = fpath+'/log'
utils.mkdirs(logpath)
logging.basicConfig(filename=logpath+'/info.log',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

app = Flask(__name__, static_url_path='')

@app.route('/pi/info', methods=['GET'])
def get_pi_info():
    info = pi_info.getPiInfo()
    return jsonify(info)

aquarium = None
@app.route('/aquarium', methods=['GET'])
def get_aquarium_status():
    global aquarium
    if aquarium is None:
        raise ServiceException("Unsupported")
    return jsonify(aquarium.get_status())


@app.route('/aquarium', methods=['POST'])
def set_aquarium_runmode():
    global aquarium
    if aquarium is None:
        raise ServiceException("Unsupported")
    action = request.args.get('action').strip()
    if action == 'swmode':
        mode = aquarium.get_runmode()
        if mode == 1:
            aquarium.set_runmode(0)
        else:
            aquarium.set_runmode(1)
    elif action == 'reload':
        aquarium.reload_cfg()
    else:
        raise ServiceException("Unsupported action")
    return jsonify(aquarium.get_status())


@app.route('/aquarium/light', methods=['POST'])
def sw_aquarium_light():
    global aquarium
    if aquarium is None:
        raise ServiceException("Unsupported")
    content = request.get_json(silent=True)
    action = content.get('action', None)
    if action is None:
        raise ServiceException("Illeagal body.")
    ret = {}
    if action == 'on':
        aquarium.light_on()
        ret['status'] = True
        return jsonify(ret)
    elif action == 'off':
        aquarium.light_off()
        ret['status'] = False
        return jsonify(ret)
    else:
        raise ServiceException("Unsupported action")


class ServiceException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super(ServiceException, self).__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(ServiceException)
def handleServiceExp(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def init():
    global aquarium
    cfg = dict()
    with open(fpath+'/pi_service_cfg.json') as cfgfile:
        cfg = json.load(cfgfile)

    if cfg['aquarium']:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        aquarium = Aquarium()


if __name__ == '__main__':
    init()
    ip = utils.get_host_ip()
    app.run(host=ip, port=18082)  # 启动socket
