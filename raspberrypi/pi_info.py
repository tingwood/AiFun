import os
import json

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
    info[3]=info[3].replace("%","")
    return info

def getPiInfo():
    RaspiInfo = {}
    RaspiInfo['CPUtemp'] = getCPUtemperature()
    RaspiInfo['RAMinfo'] = getRAMinfo()
    RaspiInfo['DISKinfo'] = getDiskinfo()
    #RaspiInfo['CPUuse'] = getCPUinfo()
    return RaspiInfo

if __name__ == '__main__':    
    # 必须转化为标准 JSON 格式备用，下文有解释
    print(json.dumps(RaspiInfo))
