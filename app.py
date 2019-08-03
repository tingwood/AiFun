# -*- coding: UTF-8 -*-
import urllib.request as http
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import json
import re
import random
import logging
import raspberrypi.pi_actions as pi

app = Flask(__name__)

logging.basicConfig(filename='./log/info.log', \
                    filemode='w', \
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', \
                    datefmt='%H:%M:%S', \
                    level=logging.INFO)


@app.route('/smarthome', methods=['GET'])
def hello():
    return "Hello"


@app.route('/smarthome/pi', methods=['POST'])
def pi_action():
    action = request.args.get('action').strip()
    if action == 'watering':
        pi.watering()
    elif action == 'snapshot':
        pi.take_pic()
    else:
        raise ServiceException('Unsupport action')


class ServiceException(Exception):
    status_code = 500

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
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18082)  # 启动socket
