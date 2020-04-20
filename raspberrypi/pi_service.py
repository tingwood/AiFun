# -*- coding: UTF-8 -*-
import os, sys
from flask import Flask, request, jsonify
import json
import logging
import RPi.GPIO as GPIO
from fishtank import Fishtank
import pi_info

#o_path=os.getcwd()
fpath=os.path.dirname(os.path.abspath(__file__))    #pi_service dir 
sys.path.append(fpath+"/../")
from utils import utils

logpath=fpath+'/log'
utils.mkdirs(logpath)
logging.basicConfig(filename=logpath+'/info.log',\
                            filemode='w',\
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',\
                            datefmt='%H:%M:%S',\
                            level=logging.INFO)

app = Flask(__name__, static_url_path='')

@app.route('/pi/info', methods=['GET'])
def get_pi_info():
    info = pi_info.getPiInfo()
    return jsonify(info)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#s1-22, s2-18, s3-17, s4-27
#s1-heater, s2-pump_ext, s3-uv
fishtank = Fishtank(0, 27, 18, 17, 22)

@app.route('/fishtank', methods=['GET'])
def get_fishtank_status():
    return jsonify(fishtank.get_status())


@app.route('/fishtank', methods=['POST'])
def set_fishtank_runmode():
    action = request.args.get('action').strip()
    if action == 'swmode':
        mode = fishtank.get_runmode()
        if mode == 1:
            fishtank.set_runmode(0)
        else:
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
    #cfg = dict()    
    #with open(fpath+'/pi_service.cfg') as cfgfile:
    #    cfg = json.load(cfgfile)
    
    
