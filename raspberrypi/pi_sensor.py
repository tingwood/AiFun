#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time
import os
import logging as log
#import thread
import threading
import Adafruit_DHT


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
        pins = [pin]
        super(Servo, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)
        if self.pwm is None:
            self.pwm = GPIO.PWM(self.pins[0], 50)
            log.debug("Servo pmw inited.")

    def __del__(self):
        if self.pwm is None:
            return
        self.pwm.stop()
        self.pwm = None

    def angle(self, degree):
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
    seg_asc = [
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 0~15
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 16~31
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xbf, 0xff, 0xff,  # 32~47
        0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 48~63
        0xff, 0x88, 0x83, 0xc6, 0xa1, 0x86, 0x8e, 0x90, 0x89, 0xf9, 0xf1, 0x8f, 0xc7, 0xff, 0xab, 0xa3,  # 64~79
        0x8c, 0x98, 0x88, 0x92, 0x87, 0xc1, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 80~95
        0xff, 0x88, 0x83, 0xa7, 0xa1, 0x86, 0x8e, 0x90, 0x8b, 0xf9, 0xf1, 0x8f, 0xc7, 0xff, 0xab, 0xa3,  # 96~111
        0x8c, 0x98, 0x88, 0x92, 0x87, 0xe3, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 112~127
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 128~143
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 144~159
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 160~175
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 176~191
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 192~207
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 208~223
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,  # 224~239
        0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]  # 240~255
    _loc = [0x08, 0x04, 0x02, 0x01]
    #loc = [0x01,0x02,0x04,0x08]
    _running = False
    _work_thread = None

    def __init__(self, a, b, c, d, e, f, g, dp, d1, d2, d3, d4):
        pins = [a, b, c, d, e, f, g, dp, d1, d2, d3, d4]
        self._running = False
        super(LED_3461BS, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT, initial=GPIO.LOW)

    def _set_seg_code(self, val):
        GPIO.output(self.pins[0], val & 0x01)
        GPIO.output(self.pins[1], val & 0x02)
        GPIO.output(self.pins[2], val & 0x04)
        GPIO.output(self.pins[3], val & 0x08)
        GPIO.output(self.pins[4], val & 0x10)
        GPIO.output(self.pins[5], val & 0x20)
        GPIO.output(self.pins[6], val & 0x40)
        GPIO.output(self.pins[7], val & 0x80)  # dp

    def _set_loc(self, index):
        loc = self._loc[index]
        GPIO.output(self.pins[8], loc & 0x08)
        GPIO.output(self.pins[9], loc & 0x04)
        GPIO.output(self.pins[10], loc & 0x02)
        GPIO.output(self.pins[11], loc & 0x01)

    def _show_thread(self, content):
        self._running = True
        # remove dot in string
        nodot = []
        length = 0
        for i in range(0, len(content)):
            if content[i] != '.':
                nodot.append(self.seg_asc[ord(content[i])])
                length = length+1
            else:
                nodot[length-1] = nodot[length-1] & 0x7f  # show dp
        if length > 4:
            nodot = [0xff, 0xff, 0xff, 0xff] + nodot + \
                [0xff, 0xff, 0xff, 0xff]  # add four space
            length = length + 4
            while(self._running):
                for i in range(0, length):
                    val = nodot[i:i+4]
                    for cnt in range(0, 25):
                        for j in range(0, 4):
                            self._set_seg_code(val[j])
                            self._set_loc(j)
                            time.sleep(0.003)
        else:
            while(self._running):
                for i in range(0, length):
                    self._set_seg_code(nodot[i])
                    self._set_loc(i+4-length)
                    time.sleep(0.003)
        GPIO.output(self.pins, GPIO.LOW)

    def show(self, val):
        self.off()
        content = str(val)
        self._work_thread = threading.Thread(
            target=self._show_thread, args=[content])
        self._work_thread.start()

    def off(self):
        self._running = False
        if self._work_thread is None:
            return
        self._work_thread.join()
        self._work_thread = None


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
    calib = 0  # calibration of sensor

    def __init__(self, serial, calib):
        self.serial = serial
        self.calib = calib

    def get_temperature(self):
        temperature = -100
        fpath = "/sys/bus/w1/devices/" + self.serial + "/w1_slave"
        if not os.path.exists(fpath):
            return temperature
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


class Relay(Sensor):
    '''
    Relay:
    Connection with Raspi:
    VCC(DC+)：5V, pin2 or pin4
    GND(DC-)：GND, pin 6
    IN：GPIO, default GPIO.HIGH to trig

    Output Control：
    NO： normal open
    COM：common
    NC： normal close

    Trigger jumpper：
    A jumpper can be set using GPIO.HIGH or GPIO.LOW to trig relay
    '''
    __trigger_val = False
    isClose = False

    def __init__(self, pin, reverse=False):
        pins = [pin]
        super(Relay, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)
        if reverse:
            self.__trigger_val = GPIO.LOW
        else:
            self.__trigger_val = GPIO.HIGH

    def close(self):
        GPIO.output(self.pins[0], self.__trigger_val)
        self.isClose = True

    def open(self):
        GPIO.output(self.pins[0], not(self.__trigger_val))
        self.isClose = False


class Ada_DHT11(Sensor):
    '''
    https://blog.csdn.net/xindoo/article/details/53544699
    GPIO connect to 'Data' pin
    '''
    sensor = None

    def __init__(self, pin):
        pins = [pin]
        super(Ada_DHT11, self).__init__(pins)
        self.sensor = Adafruit_DHT.DHT11

    # return humidity and temperature
    def get_hum_temp(self):
        humidity, temperature = Adafruit_DHT.read_retry(
            self.sensor, self.pins[0])
        if humidity is not None and temperature is not None:
            #print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
            return humidity, temperature, True
        else:
            #print('Failed to get reading. Try again!')
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

        # while GPIO.input(pin) == GPIO.HIGH:
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
        # print(data)

        humidity = 0
        humidity_point = 0
        temperature = 0
        temperature_point = 0
        check = 0

        m = [128, 64, 32, 16, 8, 4, 2, 1]
        th = 15  # threshold
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


class Distancer(Sensor):
    '''
    https://blog.csdn.net/weixin_41860080/article/details/86766856
    HY-SRF05 HY-SR04
    '''
    _running = False
    _work_thread = None
    __interval = 0.2
    __stime = 0.
    __etime = 0.
    __measuring = False

    def __init__(self, trigpin, echopin, interval=0.2):
        pins = [trigpin, echopin]
        if interval > 0.01:
            self.__interval = interval
        super(Distancer, self).__init__(pins)
        GPIO.setup(self.pins[0], GPIO.OUT)
        GPIO.setup(self.pins[1], GPIO.IN)
        time.sleep(0.02)
        GPIO.output(self.pins[0], GPIO.LOW)
        time.sleep(0.5)
        #GPIO.add_event_detect(self.pins[1], GPIO.BOTH)
        #GPIO.add_event_callback(self.pins[1], self.__timer)

    def __del__(self):
        self._running = False
        if self._work_thread is None:
            return
        self._work_thread.join()
        self._work_thread = None

    def __timer(self, chn):
        if not(self.__measuring):
            return
        if GPIO.input(chn) == GPIO.LOW:
            self.etime = time.time()
            self.__measuring = False
        else:
            self.stime = time.time()

    def get_distance(self):
        start_time = 0.
        end_time = 0.
        distance = -1
        GPIO.output(self.pins[0], GPIO.HIGH)
        time.sleep(0.0001)
        GPIO.output(self.pins[0], GPIO.LOW)
        # cnt=0
        while GPIO.input(self.pins[1]) == GPIO.LOW:
            start_time = time.time()
            # cnt=cnt+1
        # cnt=0
        while GPIO.input(self.pins[1]) == GPIO.HIGH:
            end_time = time.time()
            # cnt=cnt+1
        t = end_time - start_time
        if t > 0 and start_time > 0 and end_time > 0:
            distance = 17150 * t
            log.debug("Measured Distance is: %s cms", distance)
        else:
            log.debug("Measured distance failed")
        return distance

    def __start(self):
        self.__measuring = True
        self.stime = 0.
        self.etime = 0.

    def get_distance1(self):
        GPIO.output(self.pins[0], GPIO.HIGH)
        time.sleep(0.0001)
        self.__start()
        GPIO.output(self.pins[0], GPIO.LOW)
        # time.sleep(0.05)
        distance = -1
        print(self.stime, self.etime)
        if self.etime > 0 and self.stime > 0:
            t = self.etime - self.stime
            distance = 17150 * t
            log.debug("Measured Distance is: %s cms", distance)
        else:
            log.debug("Measured Distance failed")
        return distance


class HCSR04(Distancer):
    def __init__(self, trigpin, echopin):
        super(HCSR04, self).__init__(trigpin, echopin)


class HYSRF05(Distancer):
    def __init__(self, trigpin, echopin):
        super(HYSRF05, self).__init__(trigpin, echopin)


class OnePinSensor(Sensor):
    '''
    the base class of one input sensor
    '''

    def __init__(self, pin, pull_mode=GPIO.PUD_UP):
        pins = [pin]
        super(OnePinSensor, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=pull_mode)

    def isLow(self):
        if GPIO.input(self.pins[0]) == GPIO.LOW:
            return True
        else:
            return False

    def isHigh(self):
        return not(self.isLow())


class SoilSensor(OnePinSensor):
    '''
    Soil humidity sensor
    dry: output GPIO.HIGH
    wet: output GPIO.LOW (DO-LED will light)
    '''
    sample = 10  # sample times
    dry_th = 8  # dry threshold
    wet_th = 2  # wet threshold

    def __init__(self, pin):
        super(SoilSensor, self).__init__(pin, GPIO.PUD_DOWN)
        # if sample > 0:
        #    self.sample = sample
        #    self.dry_th = sample * 0.8
        #    self.wet_th = sample * 0.2

    def _measure(self):
        val = 0
        for i in range(0, self.sample):
            val += GPIO.input(self.pins[0])
            time.sleep(0.01)
        return val

    def isDry(self):
        val = self._measure()

        if val >= self.dry_th:  # dry
            return True
        else:
            return False

    def isWet(self):
        val = self._measure()

        if val <= self.wet_th:  # wet
            return True
        else:
            return False


class Tracker(OnePinSensor):
    '''
    Infrared tracker sensor
    if the reflection is strong enough, output GPIO.HIGH
    otherwise output GPIO.LOW (e.g. detect black line)
    '''

    def __init__(self, pin):
        super(Tracker, self).__init__(pin, GPIO.PUD_DOWN)


class BodyDetector(OnePinSensor):
    '''
    if detect human body, the input is GPIO.LOW
    '''

    def __init__(self, pin):
        super(BodyDetector, self).__init__(pin)

    def detected(self):
        return super(BodyDetector, self).isLow()


class ObjDetector(OnePinSensor):
    '''
    if detect obstacle, the input is GPIO.LOW
    '''

    def __init__(self, pin):
        super(ObjDetector, self).__init__(pin)

    def detected(self):
        return super(ObjDetector, self).isLow()


class TouchSwitcher(OnePinSensor):
    '''
    触摸开关
    if touch, the input is GPIO.LOW
    '''
    status = False  # false - off, true - on
    _on_cb = None  # switch on callback
    _off_cb = None  # switch off callback
    _cb_thread = None  # callback thread
    _running = False

    def __init__(self, pin, on_callback=None, off_callback=None):
        super(TouchSwitcher, self).__init__(pin, GPIO.PUD_UP)
        self.status = False
        self._on_cb = on_cb
        self._off_cb = off_cb
        self._cb_thread = threading.Thread(target=self._touch)
        self._running = True
        cb_thread.start()

    def __del__(self):
        self._running = False
        if self.cb_thread is None:
            return
        self.cb_thread.join()

    def _touch(self):
        while (self._running):
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
    _running = False
    _work_thread = None
    _light_status = [0, 0, 0]

    def __init__(self, rpin, gpin, bpin):
        pins = [rpin, gpin, bpin]
        super(RGBLed, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)

    def red(self):
        self._light_status = [1, 0, 0]
        GPIO.output(self.pins, self._light_status)

    def green(self):
        self._light_status = [0, 1, 0]
        GPIO.output(self.pins, self._light_status)

    def blue(self):
        self._light_status = [0, 0, 1]
        GPIO.output(self.pins, self._light_status)

    def off(self):
        self._running = False
        self._light_status = [0, 0, 0]
        if self._work_thread is not None:
            self._work_thread.join()
            self._work_thread = None
        GPIO.output(self.pins, [0, 0, 0])

    def red_blink(self, on=0.5, off=0.5):
        self._light_status = [1, 0, 0]
        self._start_thread(on, off)

    def green_blink(self, on=0.5, off=0.5):
        self._light_status = [0, 1, 0]
        self._start_thread(on, off)

    def blue_blink(self, on=0.5, off=0.5):
        self._light_status = [0, 0, 1]
        self._start_thread(on, off)

    def _start_thread(self, on=0.5, off=0.5):
        if self._work_thread is None:
            self._work_thread = threading.Thread(
                target=self._blink, args=[on, off])
            self._work_thread.start()

    def _blink(self, on, off):
        self._running = True
        while self._running:
            GPIO.output(self.pins, self._light_status)
            time.sleep(on)
            GPIO.output(self.pins, [0, 0, 0])
            time.sleep(off)


def test_DHT11():
    dht = Ada_DHT11(4)
    hum, temp, chk = dht.get_hum_temp()

    if chk:
        print("temperature :", temp, "*C, humidity:", hum, "%")
    else:
        print("check false")


def test_relay():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    relay = Relay(18)
    relay.trigger()
    time.sleep(2)
    relay.untrigger()
    time.sleep(2)
    GPIO.cleanup()


def test_RGB():
    rgb = RGBLed(21, 17, 27)
    rgb.red_blink(0.8, 0.2)
    time.sleep(10)
    rgb.green_blink()
    time.sleep(10)
    rgb.blue_blink()
    time.sleep(10)
    rgb.off()


def test_Tracker():
    sen = Tracker(4)
    while True:
        print(sen.reflect())
        time.sleep(1)


def test_DS18B20():
    sen = DS18B20('28-01191a61480c')
    print(sen.get_temperature())


def test_Ultrasonic():
    sen = HCSR04(3, 2)
    print(sen.get_distance())


def test_obstacle():
    sen = ObjDetector(13)
    print(sen.detected())


def test_3461BS():
    '''
     1  a  f  2  3  b 
     e  d  dp c  g  4
    '''
    sen = LED_3461BS(19, 11, 12, 20, 21, 13, 7, 16, 26, 6, 5, 8)
    sen.show('23.88')
    time.sleep(20)
    sen.off()
    time.sleep(1)


def test_servo():
    servo = Servo(26)
    servo.angle(0)
    time.sleep(2)
    servo.angle(90)
    time.sleep(2)
    servo.angle(180)
    time.sleep(2)


def test_main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    test_DHT11()
    # test_RGB()
    # test_Tracker()
    # test_DS18B20()
    # test_Ultrasonic()
    # test_3461BS()
    # test_servo()
    # test_obstacle()
    GPIO.cleanup()


if __name__ == '__main__':
    test_main()
