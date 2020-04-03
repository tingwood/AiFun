# -*- coding: UTF-8 -*-
from flask import Flask, request, jsonify
import json
import logging
import RPi.GPIO as GPIO
from fishtank import Fishtank

app = Flask(__name__)
logging.basicConfig(filename='./log/info.log',\
                            filemode='w',\
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',\
                            datefmt='%H:%M:%S',\
                            level=logging.INFO)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
fishtank = Fishtank(0,4,17,18,27)
@app.route('/fishtank', methods=['GET'])
def get_fishtank_status():
    ret = fishtank.get_status()
    print(ret)
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

