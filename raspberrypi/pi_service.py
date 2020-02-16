# -*- coding: UTF-8 -*-
import urllib.request as http
from bs4 import BeautifulSoup
from flask import Flask,request,jsonify
import json
import re
import random
import logging
import pi_actions as pi

app=Flask(__name__) 

logging.basicConfig(filename='./log/info.log',\
                            filemode='w',\
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',\
                            datefmt='%H:%M:%S',\
                            level=logging.INFO)

@app.route('/pi',methods=['GET'])
def hello():
    action= request.args.get('action').strip()
    if action=="hello":
        return "Hello"
    elif action=="temp":
        hum,temp=pi.get_temp();
        return "temp",temp
    else:
        raise ServiceException("Unsupport actions", status_code=500)
    

@app.route('/book',methods=['GET'])      
def bookByIsbn():
    isbn = request.args.get('isbn').strip()
    logging.info(request)
    if isbn is None:
        raise ServiceException('Missing parameters.', status_code=500)
    else:        
        isIsbn=isbnRegex.match(isbn)
        if isIsbn is None:
            raise ServiceException('Invalid isbn.', status_code=500)
        
        ret={}
        try:
            book=doubanCrawler(isbn)
            #print book
            ret=dict(ret.items()+book.items())
        except Exception as e:
            logging.info('Creep bookinfo from douban failed. Reason as below:')
            logging.info(e)
        '''
        try:
            book=goodReadsCrawler(isbn)
            #print book
            ret=dict(ret.items()+book.items())
        except Exception as e:
            logging.info('Creep bookinfo from goodreads failed. Reason as below:')
            logging.info(e)
        '''
        if ret=={}:
            raise ServiceException("Book not found", status_code=404)
        return jsonify(ret)


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
    app.run(host='0.0.0.0',port=18082)              #启动socket




