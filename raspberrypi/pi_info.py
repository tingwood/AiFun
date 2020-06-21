# -*- coding: UTF-8 -*-
import os
import json
from pi_sensor import LED_3461BS
import RPi.GPIO as GPIO
import time


# Return CPU temperature as a float
def getCPUtemperature():
    f = os.popen("cat /sys/class/thermal/thermal_zone0/temp")
    temp = int(f.readline().strip())/1000
    return round(temp, 1)

# Return RAM information (unit=MB) in a list
# Index 0: total RAM
# Index 1: used RAM
# Index 2: free RAM


def getRAMinfo():
    f = os.popen("free | awk '/Mem/ {print $2,$3,$4}'")
    info = f.readline().split()
    info = [round(int(i)/1024, 1) for i in info]
    return info


'''
# Return % of CPU used by user as float
def getCPUinfo():
    # Docker外部 info = os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()
    # Docker内部 info = os.popen("top -n1 | awk '/CPU:/ {print $2}'").readline().strip()
    if info:
        return float(info)
    else:
    	# 未获取到信息，返回默认错误值
        return -1.0
'''

# Return information about disk space as a list (unit included)
# Index 0: total disk space
# Index 1: used disk space
# Index 2: remaining disk space
# Index 3: percentage of disk used


def getDiskinfo():
    f = os.popen("df -h /")
    info = f.readlines()[1].split()[1:5]
    info[3] = info[3].replace("%", "")
    return info


def getPiInfo():
    RaspiInfo = {}
    RaspiInfo['CPUtemp'] = getCPUtemperature()
    RaspiInfo['RAMinfo'] = getRAMinfo()
    RaspiInfo['DISKinfo'] = getDiskinfo()
    #RaspiInfo['CPUuse'] = getCPUinfo()
    return RaspiInfo


def fanCtrl():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    '''
     1  a  f  2  3  b 
     e  d  dp c  g  4
    '''
    led = LED_3461BS(19, 11, 12, 20, 21, 13, 7, 16, 26, 6, 5, 8)
    pin = 14
    GPIO.setup(pin, GPIO.OUT)
    on = False

    temp = getCPUtemperature()
    if temp >= 50:
        GPIO.output(pin, on)
        led.show('On')
        time.sleep(3)
    if temp < 42:
        GPIO.output(pin, not(on))
        led.show('Off')
        time.sleep(3)

    led.off()


if __name__ == '__main__':
    print(json.dumps(getPiInfo()))
    fanCtrl()
