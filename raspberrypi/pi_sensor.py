#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time
import os
import logging as log
#import thread
import threading


class Sensor(object):
    '''
    Sensor base class
    '''
    pins = []  # sensor connected pins with raspberry pi

    def __init__(self, pins):
        self.pins = pins

class Servo(Sensor):    
    pwm = None
    def __init__(self, pin):
        pins=[pin]
        super(Servo, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)
        if self.pwm is None:
            self.pwm=GPIO.PWM(self.pins[0],50)
            log.debug("Servo pmw inited.")
            
            
    
    def __del__(self):
        if self.pwm is None:
            return
        self.pwm.stop()
        
    def angle(self,degree):
        if self.pwm is None:
            log.error("Servo pmw is None")
            return
        self.pwm.start(2.5)
        dc = degree / 18. + 2.5
        self.pwm.ChangeDutyCycle(dc)
        time.sleep(1)
        self.pwm.stop()
        log.debug("Servo angle %s", degree)
        
        

class LED_3461BS(Sensor):
    '''
     1  a  f  2  3  b 
     e  d  dp c  g  4
     
      --A--
    F|     |B
      --G--
    E|     |C
      --D--  .DP       
    '''
    seg_asc=[
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #0~15
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #16~31
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xbf,0xff,0xff, #32~47
    0xc0,0xf9,0xa4,0xb0,0x99,0x92,0x82,0xf8,0x80,0x90,0xff,0xff,0xff,0xff,0xff,0xff, #48~63
    0xff,0x88,0x83,0xc6,0xa1,0x86,0x8e,0x90,0x89,0xf9,0xf1,0x8f,0xc7,0xff,0xab,0xa3, #64~79
    0x8c,0x98,0x88,0x92,0x87,0xc1,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #80~95
    0xff,0x88,0x83,0xa7,0xa1,0x86,0x8e,0x90,0x8b,0xf9,0xf1,0x8f,0xc7,0xff,0xab,0xa3, #96~111
    0x8c,0x98,0x88,0x92,0x87,0xe3,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #112~127
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #128~143
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #144~159
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #160~175
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #176~191
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #192~207
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #208~223
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff, #224~239
    0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff] #240~255
    loc = [0x08,0x04,0x02,0x01]
    #loc = [0x01,0x02,0x04,0x08]
    on=False
    content=''
    def __init__(self, a,b,c,d,e,f,g,dp,d1,d2,d3,d4):
        pins=[a,b,c,d,e,f,g,dp,d1,d2,d3,d4]
        self.on=False
        super(LED_3461BS, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT , initial=GPIO.LOW)
    
    def __show_char(self,ch,dp=False):        
        val = self.seg_asc[ord(ch)]        
        GPIO.output(self.pins[0], val & 0x01)
        GPIO.output(self.pins[1], val & 0x02)
        GPIO.output(self.pins[2], val & 0x04)
        GPIO.output(self.pins[3], val & 0x08)
        GPIO.output(self.pins[4], val & 0x10)
        GPIO.output(self.pins[5], val & 0x20)
        GPIO.output(self.pins[6], val & 0x40)
        #GPIO.output(self.pins[7], val & 0x80)
        GPIO.output(self.pins[7], not(dp))   #dp
        
    def __show_loc(self, index):
        loc=self.loc[index]
        GPIO.output(self.pins[8], loc & 0x08)
        GPIO.output(self.pins[9], loc & 0x04)
        GPIO.output(self.pins[10], loc & 0x02)
        GPIO.output(self.pins[11], loc & 0x01)
    
    def __show_thread(self):
        self.on=True
        a = self.content
        length=len(a)
        if length>4:
            return
        else:
            while(self.on):
                for i in range(0,length):                
                    self.__show_loc(i+4-length)
                    self.__show_char(a[i],False)
                    time.sleep(0.004)
                    
    def show(self,val):
        self.content=str(val)
        t1=threading.Thread(target=self.__show_thread)
        t1.start()
                    
    def off(self):
        self.on=False
        GPIO.output(self.pins, GPIO.LOW)
        
class DS18B20():
    '''
    https://zhuanlan.zhihu.com/p/69890507
    pi@raspberrypi:~ $ sudo nano /boot/config.txt
    在dtoverlay=dwc2之前添加一行：
    dtoverlay=w1-gpio-pullup,gpiopin=4
    加载2个模块
    pi@raspberrypi:~ $ sudo modprobe w1-gpio
    pi@raspberrypi:~ $ sudo modprobe w1-therm
    查看温度传感器DS18B20设备
    pi@raspberrypi:~ $ cd /sys/bus/w1/devices/
    依次在终端输入以下命令：
    pi@raspberrypi:/sys/bus/w1/devices $ cd 28-000004d618fa
    pi@raspberrypi:/sys/bus/w1/devices/28-000004d618fa $ cat w1_slave
    '''
    serial = ''
    calib = 0  #calibration of sensor

    def __init__(self, serial, calib):
        self.serial = serial
        self.calib = calib

    def get_temperature(self):
        fpath="/sys/bus/w1/devices/" + self.serial + "/w1_slave"
        if not os.path.exists(fpath):
            return -50
        tfile = open(fpath)
        # Read all of the text in the file.
        text = tfile.read()
        # close the file
        tfile.close()
        # Split the text with new lines (\n) and select the second line.
        secondline = text.split("\n")[1]
        # Split the line into words, referring to the spaces, and select the 10th word (counting from 0).
        temperaturedata = secondline.split(" ")[9]
        # The first two characters are "t=", so get rid of those and convert the temperature from a string to a number.
        temperature = float(temperaturedata[2:])
        # Put the decimal point in the right place and display it.
        temperature = temperature / 1000 + self.calib 
        return temperature


class SoilSensor(Sensor):
    '''
    Soil humidity sensor
    dry: output GPIO.HIGH
    wet: output GPIO.LOW (DO-LED will light)
    '''
    sample = 20  # sample times
    dry_th = 0  # dry threshold
    wet_th = 0  # wet threshold

    def __init__(self, pin, sample=20):
        pins = [pin]
        super(SoilSensor, self).__init__(pins)
        if sample > 0:
            self.sample = sample
        self.dry_th = sample * 0.8
        self.wet_th = sample * 0.2
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def isdry(self):
        val = 0
        for i in range(0, self.sample):
            val += GPIO.input(self.pins[0])
            time.sleep(0.2)

        if val >= self.dry_th:  # dry
            return True
        else:
            return False

    def iswet(self):
        val = 0
        for i in range(0, self.sample):
            val += GPIO.input(self.pins[0])
            time.sleep(0.2)

        if val <= self.wet_th:  # wet
            return True
        else:
            return False


class Relay(Sensor):
    '''
    Relay:
    Connection with Raspi:
    VCC(DC+)：5V, pin2 or pin4
    GND(DC-)：GND, pin 6
    IN：GPIO, pin11 GPIO.LOW or GPIO.HIGH

    Output Control：
    NO： diconnect in usual, connect when trigger
    COM：common
    NC： connect in usual, disconnect when trigger

    Trigger jumpper：
    A jumpper can be set using GPIO.LOW or GPIO.HIGH to relay trigger
    '''
    reverse = False
    def __init__(self, pin, reverse=False):
        pins = [pin]
        super(Relay, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)
        self.reverse=reverse

    def close(self):
        if self.reverse:
            GPIO.output(self.pins[0], GPIO.LOW)
        else:
            GPIO.output(self.pins[0], GPIO.HIGH)

    def open(self):
        if self.reverse:
            GPIO.output(self.pins[0], GPIO.HIGH)
        else:
            GPIO.output(self.pins[0], GPIO.LOW)

            
class Tracker(Sensor):
    '''
    Infrared tracker sensor
    if the reflection is strong enough, output GPIO.HIGH
    otherwise output GPIO.LOW (e.g. detect black line)
    '''
    val = 1
    def __init__(self, pin, reverse=False):
        pins = [pin]
        self.val = (reverse==False) and 1 or 0
        super(Tracker, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    def ontrack(self):
        if GPIO.input(self.pins[0]) == self.val:
            return True
        else:
            return False
            
    def offtrack(self):
        return not(self.ontrack)

class DHT111(Sensor):
    '''
    https://blog.csdn.net/xindoo/article/details/53544699
    GPIO connect to 'Data' pin
    '''
    t_last = 0
    time_diffs = []

    def __init__(self, pin):
        pins = [pin]
        super(DHT111, self).__init__(pins)

    def reset(self):
        self.time_diffs = []
        self.t_last = 0

    def record_time(self, pin):
        t = time.time()
        self.time_diffs.append(t - self.t_last)
        self.t_last = t
        print("detect falling on pin ", pin)

    # return humidity and temperature
    def get_hum_temp(self):
        pin = self.pins[0]
        self.reset()
        data = []
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
        time.sleep(0.02)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.02)
        GPIO.output(pin, GPIO.HIGH)

        GPIO.setup(pin, GPIO.IN)
        GPIO.add_event_detect(pin, GPIO.FALLING)
        GPIO.add_event_callback(pin, self.record_time)
        time.sleep(1)

        length = len(self.time_diffs)
        print("length is ", length)
        if length == 43:
            for t in self.time_diffs[length - 40:length]:
                data.append(1 if t > 0.000085 else 0)

            humidity_bit = data[0:8]
            humidity_point_bit = data[8:16]
            temperature_bit = data[16:24]
            temperature_point_bit = data[24:32]
            check_bit = data[32:40]

            humidity = 0
            humidity_point = 0
            temperature = 0
            temperature_point = 0
            check = 0
            m = [128, 64, 32, 16, 8, 4, 2, 1]
            for i in range(8):
                humidity += humidity_bit[i] * m[i]
                humidity_point += humidity_point_bit[i] * m[i]
                temperature += temperature_bit[i] * m[i]
                temperature_point += temperature_point_bit[i] * m[i]
                check += check_bit[i] * m[i]

            tmp = humidity + humidity_point + temperature + temperature_point

            if check == tmp:
                print("temperature :", temperature, "*C, humidity:", humidity,
                      "%")
                return humidity, temperature, True
        return 0, 0, False


class DHT11(Sensor):
    '''
    https://blog.csdn.net/xindoo/article/details/53544699
    GPIO connect to 'Data' pin
    '''
    def __init__(self, pin):
        pins = [pin]
        super(DHT11, self).__init__(pins)

    # return humidity and temperature
    def get_hum_temp(self):
        pin = self.pins[0]
        data = []
        i = 0

        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
        time.sleep(0.02)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.02)
        GPIO.output(pin, GPIO.HIGH)

        GPIO.setup(pin, GPIO.IN)

        #while GPIO.input(pin) == GPIO.HIGH:
        #    continue
        timeout = 5000
        while GPIO.input(pin) == GPIO.LOW and timeout > 0:
            timeout -= 1

        timeout = 5000
        while GPIO.input(pin) == GPIO.HIGH and timeout > 0:
            timeout -= 1

        while i < 40:
            cnt = 0
            timeout = 5000
            while GPIO.input(pin) == GPIO.LOW and timeout > 0:
                timeout -= 1
            while GPIO.input(pin) == GPIO.HIGH:
                cnt += 1
                if cnt > 100:
                    break
            data.append(cnt)
            i += 1
        #print(data)

        humidity = 0
        humidity_point = 0
        temperature = 0
        temperature_point = 0
        check = 0

        m = [128, 64, 32, 16, 8, 4, 2, 1]
        th = 15  #threshold
        for i in range(8):
            humidity += (0 if data[i] < th else 1) * m[i]
            humidity_point += (0 if data[i + 8] < th else 1) * m[i]
            temperature += (0 if data[i + 16] < th else 1) * m[i]
            temperature_point += (0 if data[i + 24] < th else 1) * m[i]
            check += (0 if data[i + 32] < th else 1) * m[i]
        #print("temperature :", temperature, "*C, humidity:", humidity, "%", " tp ",temperature_point," hp ",humidity_point," check ",check)

        if check == humidity + humidity_point + temperature + temperature_point:
            return humidity, temperature, True
        else:
            return 0, 0, False

    def get_temperature(self):
        hum, temp = self.get_hum_temp()
        return temp

    def get_humidity(self):
        hum, temp = self.get_hum_temp()
        return hum

    
class Ultrasonic_Distance(Sensor):
    '''
    https://blog.csdn.net/weixin_41860080/article/details/86766856
    HY-SRF05 HY-SR04
    '''
    __running = False
    __t1 = None
    __interval=0.2
    __stime=0.
    __etime=0.
    __measuring = False
    
    def __init__(self, trigpin, echopin, interval=0.2):
        pins = [trigpin, echopin]
        if interval>0.01:
            self.__interval = interval
        super(Ultrasonic_Distance, self).__init__(pins)
        GPIO.setup(self.pins[0], GPIO.OUT)
        GPIO.setup(self.pins[1], GPIO.IN)    
        time.sleep(0.02)  
        GPIO.output(self.pins[0], GPIO.LOW)
        time.sleep(0.5)
        #GPIO.add_event_detect(self.pins[1], GPIO.BOTH)
        #GPIO.add_event_callback(self.pins[1], self.__timer)
    
    def __del__(self):
        self.__running= False
        if self.__t1 is None:
            return
        self.__t1.join()
    
    def __timer(self,chn):
        if not(self.__measuring):
            return
        if GPIO.input(chn) == GPIO.LOW:
            self.etime=time.time()
            self.__measuring = False
        else:
            self.stime=time.time()
        
        
    def get_distance(self):
        start_time = 0.
        end_time = 0.
        distance = -1
        GPIO.output(self.pins[0], GPIO.HIGH)
        time.sleep(0.0001)
        GPIO.output(self.pins[0], GPIO.LOW)
        #cnt=0
        while GPIO.input(self.pins[1]) == GPIO.LOW:
            start_time = time.time()
            #cnt=cnt+1
        #cnt=0
        while GPIO.input(self.pins[1]) == GPIO.HIGH:
            end_time = time.time()
            #cnt=cnt+1
        t = end_time - start_time
        if t > 0 and start_time>0 and end_time>0:
            distance = 17150 * t
            log.debug("Measured Distance is: %s cms", distance)
        else:
            log.debug("Measured distance failed")
        return distance
    
    def __start(self):
        self.__measuring = True
        self.stime=0.
        self.etime=0.
        
    def get_distance1(self):
        GPIO.output(self.pins[0], GPIO.HIGH)
        time.sleep(0.0001)
        self.__start()
        GPIO.output(self.pins[0], GPIO.LOW)
        #time.sleep(0.05)
        distance = -1
        print (self.stime, self.etime)
        if self.etime>0 and self.stime>0:
            t = self.etime - self.stime
            distance = 17150 * t
            log.debug("Measured Distance is: %s cms", distance)            
        else:
            log.debug("Measured Distance failed")
        return distance


class HCSR04(Ultrasonic_Distance):
    def __init__(self, trigpin, echopin, interval=0.2):
        super(HCSR04, self).__init__(trigpin, echopin, interval)

class HYSRF05(Ultrasonic_Distance):
    def __init__(self, trigpin, echopin, interval=0.2):
        super(HYSRF05, self).__init__(trigpin, echopin, interval)

class InfraredObstacle(Sensor):
    '''
    if detect obstacle, the input is GPIO.LOW
    '''
    def __init__(self, pin):
        pins = [pin]
        super(InfraredObstacle, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def obstacle(self):
        if GPIO.input(self.pins[0]) == GPIO.LOW:
            return True


class TouchSwitcher(Sensor):
    '''
    触摸开关
    if touch, the input is GPIO.LOW
    '''
    status = False
    callback = None

    def __init__(self, pin, callback):
        pins = [pin]
        super(TouchSwitcher, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.status = False
        self.callback = callback

    def status(self):
        return self.status

    def __detect_touch(self):
        while 1:
            touch = False
            while GPIO.input(self.pins[0]) == GPIO.HIGH:
                continue
            while GPIO.input(self.pins[0]) == GPIO.LOW:
                touch = True
            if touch:
                self.status = not self.status


class RGBLed(Sensor):
    '''
    RGB Leb light.
    '''
    on = False

    def __init__(self, rpin, gpin, bpin):
        pins = [rpin, gpin, bpin]
        super(RGBLed, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)

    def red(self):
        self.on = True
        GPIO.output(self.pins, [1, 0, 0])

    def green(self):
        self.on = True
        GPIO.output(self.pins, [0, 1, 0])

    def blue(self):
        self.on = True
        GPIO.output(self.pins, [0, 0, 1])

    def off(self):
        GPIO.output(self.pins, [0, 0, 0])
        self.on = False

    def red_blink(self, on=0.5, off=0.5):
        thread.start_new_thread(self.blink, (self.pins[0], on, off))

    def green_blink(self, on=0.5, off=0.5):
        thread.start_new_thread(self.blink, (self.pins[1], on, off))

    def blue_blink(self, on=0.5, off=0.5):
        thread.start_new_thread(self.blink, (self.pins[2], on, off))

    def blink(self, pin, on, off):
        self.off()
        time.sleep(0.5)
        self.on = True
        while self.on:
            GPIO.output(pin, 1)
            time.sleep(on)
            GPIO.output(pin, 0)
            time.sleep(off)
