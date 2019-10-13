1. 控制浇水
2. 查看照片
3. 照片发送
4. 定期清理文件
5. 视频监控(IP Camara H264 recorder)
6. 
7. 上传文件
8. 打印文件(上传文件，后台打印)---场景不多

# Notes
## Raspberry Pi
### command
#### Config raspberry pi
sudo raspi-config
 
#### Change source.list
sudo sed -i 's#://raspbian.raspberrypi.org#s://mirrors.tuna.tsinghua.edu.cn/raspbian#g' /etc/apt/sources.list
sudo sed -i 's#://archive.raspberrypi.org/debian#s://mirrors.tuna.tsinghua.edu.cn/raspberrypi#g' /etc/apt/sources.list.d/raspi.list

#### install python 3.6
Refer to https://gist.github.com/dschep/24aa61672a2092246eaca2824400d37f

#### install raspberry gpio
pip install RPi.GPIO

## Linux
#### install samba
1. install samba server and client
sudo apt-get update
sudo apt-get install samba samba-common-bin smbclient cifs-utils

2. Mount the folder on the Raspberry Pi (as client)
smbclient -L <hostIP>       -----list sharing dir of samba server
smbclient <hostIP>/share    -----visit share dir directly

sudo mount.cifs //<hostname or IP address>/share /home/pi/share -o user=<name>

开机自动挂载匿名samba
vim /etc/fstab
//192.168.151.2/share   /151.2_share            cifs    defaults,guest  0 0

开机自动挂载非匿名samba
vim /etc/fstab
//192.168.2.2/share     /151.2_share            cifs    defaults,username=samba,password=samba


3. As samba server
3.1 mkdir shared 
3.2 sudo nano /etc/samba/smb.conf
3.3 add config in smb.conf as follow:
[share]
    path = /home/pi/shared
    read only = no
    public = yes
    writable = yes
    
## Python
### 生成requirements.txt
在查看别人的Python项目时，经常会看到一个requirements.txt文件，里面记录了当前程序的所有依赖包及其精确版本号。这个文件有点类似与Rails的Gemfile。其作用是用来在另一台PC上重新构建项目所需要的运行环境依赖。

requirements.txt可以通过pip命令自动生成和安装

生成requirements.txt文件
pip freeze > requirements.txt

安装requirements.txt依赖
pip install -r requirements.txt
