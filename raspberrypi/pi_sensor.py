#!/usr/bin/python
# -*- coding: UTF-8 -*-
import RPi.GPIO as GPIO
import time


class Sensor:
    '''
    Sensor base class
    '''
    pins = []  # sensor connected pins with raspberry pi

    def __init__(self, pins):
        self.pins = pins


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

    def __init__(self, pin):
        pins = [pin]
        super(Relay, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)

    def trigger(self):
        GPIO.output(self.pins[0], GPIO.HIGH)

    def untrigger(self):
        GPIO.output(self.pins[0], GPIO.LOW)


class InfraredTracker(Sensor):
    '''
    Infrared tracker sensor
    if the reflection is strong enough, output GPIO.HIGH
    otherwise output GPIO.LOW (e.g. detect black line)
    '''

    def __init__(self, pin):
        pins = [pin]
        super(InfraredTracker, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def getresult(self):
        return GPIO.input(self.pins[0])


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
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.04)
        GPIO.output(pin, GPIO.HIGH)

        GPIO.setup(pin, GPIO.IN)

        while GPIO.input(pin) == GPIO.LOW:
            continue
        while GPIO.input(pin) == GPIO.HIGH:
            continue
        i = 0
        while i < 40:
            cnt = 0
            while GPIO.input(pin) == GPIO.LOW:
                continue
            while GPIO.input(pin) == GPIO.HIGH:
                cnt += 1
                if cnt > 100:
                    break
            if cnt < 12:
                data.append(0)
            else:
                data.append(1)
            i += 1

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

        for i in range(8):
            humidity += humidity_bit[i] * 2 ** (7 - i)
            humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
            temperature += temperature_bit[i] * 2 ** (7 - i)
            temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
            check += check_bit[i] * 2 ** (7 - i)

        tmp = humidity + humidity_point + temperature + temperature_point

        if check == tmp:
            # print("temperature :", temperature, "*C, humidity:", humidity, "%")
            return humidity, temperature
        else:
            return 0, 0

    def get_temperature(self):
        hum, temp = self.get_hum_temp()
        return temp

    def get_humidity(self):
        hum, temp = self.get_hum_temp()
        return hum


class Ultrasonic(Sensor):
    '''
    https://blog.csdn.net/weixin_41860080/article/details/86766856
    HY-SRF05 HY-SR04
    '''

    def __init__(self, trigpin, echopin):
        pins = [trigpin, echopin]
        super(Ultrasonic, self).__init__(pins)
        GPIO.setup(self.pins[0], GPIO.OUT)
        GPIO.setup(self.pins[1], GPIO.IN)
        time.sleep(0.02)
        GPIO.output(self.pins[0], GPIO.LOW)

    def distance(self):
        GPIO.output(self.pins[0], GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.pins[0], GPIO.LOW)
        while GPIO.input(self.pins[1]) == GPIO.LOW:
            start_time = time.time()
        while GPIO.input(self.pins[1]) == GPIO.HIGH:
            end_time = time.time()
        t = end_time - start_time
        distance = 17150 * t
        print("Measured Distance is:", distance, "cms.")
        return distance


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
    callback()

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

    def __init__(self, rpin, gpin, bpin):
        pins = [rpin, gpin, bpin]
        super(RGBLed, self).__init__(pins)
        GPIO.setup(self.pins, GPIO.OUT)

    def red(self):
        GPIO.output(self.pins, [1, 0, 0])

    def green(self):
        GPIO.output(self.pins, [0, 1, 0])

    def blue(self):
        GPIO.output(self.pins, [0, 0, 1])

    def turnoff(self):
        GPIO.output(self.pins, [0, 0, 0])
