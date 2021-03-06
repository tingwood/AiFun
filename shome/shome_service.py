# -*- coding: UTF-8 -*-
import requests
from flask import Flask, request, jsonify
import json
import re
import random
import logging
import time

# import pi_actions as pi
baseUrl = '/api/shome'
ip = '0.0.0.0'
port = 18083

app = Flask(__name__, static_url_path=baseUrl)

logging.basicConfig(filename='./log/info.log',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


@app.route('/test', methods=['GET', 'POST'])
def test():
    # 获取 url 参数内容
    x = request.args.get("x")

    # 获取 form 表单内容
    y = request.form.get("y")

    # 获取 http 头部内容
    z = request.headers.get("z")
    # 获取json格式的body，返回直接就是dict类型
    content = request.get_json(silent=True)
    content.get('url', None)
    print(content)
    return ""


def get_url_arg(req, key):
    arg = req.args.get(key, None)
    if arg is None:
        raise ServiceException("Request error", "Illeagel parameters.")
    return arg


def get_header(req, key):
    arg = req.headers.get(key, None)
    if arg is None:
        raise ServiceException("Request error", "Illeagel header.")
    return arg


iClients = dict()


# client register periodical as heartbeat (1s)
@app.route('/clients', methods=['POST'])
def activeClient():
    content = request.get_json(silent=True)
    url = content.get('url', None)  # ip:port
    if url is None:
        raise ServiceException("Param Error", payload="Missing url.")
    content['status'] = 0  # 0-active, 1-inactive ...
    content['timestamp'] = time.time()
    iClients[url] = content


# if client's heartbeat lost 10s will inactive client
def inactiveClient():
    t = time.time() - 10
    for value in iClients.values():
        ts = value['timestamp']
        if ts < t:
            value['status'] = 1


switchers = dict()
with open('switcher.txt') as jsonfile:
    switchers = json.load(jsonfile)


@app.route('/switchers/<id>', methods=['POST'])
def switcherAction(id):
    sw = switchers.get(id, None)
    if sw is None:
        raise ServiceException("Switcher not Found",
                               payload="Please check switcher ID.")

    sw.get('')
    action = get_url_arg(request, 'action').strip()
    if action == 'on' or action == 'off':
        cmd = {'dev': id, 'cmd': action}
        sendCommand(clt, cmd)
    else:
        raise ServiceException("Unsupport actions")


@app.route('/switchers', methods=['POST'])
def addSwitcher():
    content = request.get_json(silent=True)
    id = content.get('id', None)
    if id is None:
        raise ServiceException("Param Error", payload="Missing switcher ID.")
    switchers[id] = content
    with open('switcher.txt', 'w') as outfile:
        json.dump(switchers, outfile)
    return jsonify(content)


@app.route('/switchers/<id>', methods=['PUT'])
def updSwitcher(id):
    if id is None or id == '':
        raise ServiceException("Param Error", payload="Missing switcher ID.")
    content = request.get_json(silent=True)
    content['id'] = id
    sw = switchers.get(id, None)
    if sw is None:
        raise ServiceException("Switcher not Found",
                               payload="Please check switcher ID.")
    switchers[id] = content
    return jsonify(switchers[id])


@app.route('/switchers', methods=['GET'])
def listSwitchers():
    sws = []
    for value in switchers.values():  # 取出value
        sws.append(value)
    return jsonify(sws)


@app.route('/switchers/<id>', methods=['GET'])
def getSwitcher(id):
    if id is None or id == '':
        raise ServiceException("Param Error", payload="Missing switcher ID.")
    sw = switchers.get(id, None)
    if sw is None:
        raise ServiceException("Switcher not Found",
                               payload="Please check switcher ID.")
    return jsonify(sw)


@app.route('/switchers/<id>', methods=['DELETE'])
def delSwitcher(id):
    if id is None or id == '':
        raise ServiceException("Param Error", payload="Missing switcher ID.")
    switchers.pop(id, None)
    return id


def sendCommand(iClient, command):
    url = iClient['url']
    res = requests.post(url, data=json.dumps(command))
    if res.status_code == 200:
        return True
    else:
        return False


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
def handleServiceExp(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run(host=ip, port=port)  # 启动socket
