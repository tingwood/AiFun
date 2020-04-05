# -*- coding: UTF-8 -*-
from flask import Flask, request, jsonify
import json
import logging
import RPi.GPIO as GPIO
from fishtank import Fishtank
import os
import pi_info

app = Flask(__name__)


def mkdirs(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


mkdirs('.log')
logging.basicConfig(filename='./log/info.log',\
                            filemode='w',\
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',\
                            datefmt='%H:%M:%S',\
                            level=logging.INFO)


@app.route('/pi/info', methods=['GET'])
def get_pi_info():
    info = pi_info.getPiInfo()
    return jsonify(info)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#s1-22, s2-18, s3-17, s4-27
#s1-heater, s2-pump_ext, s3-uv
fishtank = Fishtank(0, 0, 18, 17, 0)


@app.route('/fishtank', methods=['GET'])
def get_fishtank_status():
    ret = fishtank.get_status()
    return jsonify(ret)


@app.route('/fishtank', methods=['POST'])
def set_fishtank_runmode():
    mode = request.args.get('mode').strip()
    if mode == '0':
        fishtank.set_runmode(0)
    elif mode == '1':
        fishtank.set_runmode(1)
    else:
        raise ServiceException("Unsupport mode")
    return jsonify(fishtank.get_status())


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18082)  #启动socket
