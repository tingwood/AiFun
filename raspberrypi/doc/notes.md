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

#### install input

sudo apt-get install fcitx fcitx-googlepinyin fcitx-table-wubi

#### install python 3.6

Refer to <https://gist.github.com/dschep/24aa61672a2092246eaca2824400d37f>

#### change pip install source

sudo vi /etc/pip.conf
[global]
index-url = <http://mirrors.aliyun.com/pypi/simple/>
[install]
trusted-host= mirrors.aliyun.com

#### install raspberry gpio

pip install RPi.GPIO

## Linux

#### mount usb hard disk

modify fstab
/dev/sda1 /mount/path ntfs defaults,nofail,x-system.device-timeout=1,noatime 0 0
nofail -- system will continue to boot even if no hard disk, otherwise system will boot failed.

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
//192.168.151.2/share   /151.2_share            cifs    defaults,nofail,x-system.device-timeout=1  0 0

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

#### install squid

sudo apt-get install squid

sudo nano /etc/squid/conf.d/xxx
http_port 3128
cache_mem 64 MB
maximum_object_size 4 MB
cache_dir ufs /var/spool/squid 100 16 256
access_log /var/log/squid/access.log
acl localnet src 192.168.1.0/24
http_access allow localnet

#### install ss

#### install polipo

#### set static ip

修改etc目录下的dhcpcd.conf文件，在末尾加入以下代码：

interface wlan0
static ip_address=192.168.0.137/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1

## Python

### 生成requirements.txt

在查看别人的Python项目时，经常会看到一个requirements.txt文件，里面记录了当前程序的所有依赖包及其精确版本号。这个文件有点类似与Rails的Gemfile。其作用是用来在另一台PC上重新构建项目所需要的运行环境依赖。

requirements.txt可以通过pip命令自动生成和安装

生成requirements.txt文件
pip freeze > requirements.txt

安装requirements.txt依赖
pip install -r requirements.txt

# Docker installation

## way 1

sudo curl -sSL <https://get.docker.com> | sh

## way 2

## Error FAQ

docker: Got permission denied ...  解决办法: 要把用户加到docker组
将用户增加到docker用户组
sudo gpasswd -a {user} docker
退出当前用户比如切换为root，再次切换回来
sudo su
su {user}

Error response from daemon: Conflict.
$ docker ps -a
$ docker rm {qgis-desktop-2-4}

# hass docker installation

docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=MY_TIME_ZONE \
  -v /home/pi/.homeassistant:/config \
  --network=host \
  ghcr.io/home-assistant/raspberrypi3-homeassistant:stable

  docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=MY_TIME_ZONE \
  -v /home/pi/.homeassistant:/config \
  --network=host \
  ghcr.io/home-assistant/raspberrypi4-homeassistant:stable

重启homeassistant
docker restart homeassistant

# Openwrt 替换源
<https://mirrors.tuna.tsinghua.edu.cn>
src/gz openwrt_core <https://mirrors.tuna.tsinghua.edu.cn/openwrt/releases/21.02.0-rc4/targets/bcm27xx/bcm2711/packages>
src/gz openwrt_base <https://mirrors.tuna.tsinghua.edu.cn/openwrt/releases/21.02.0-rc4/packages/aarch64_cortex-a72/base>
src/gz openwrt_luci <https://mirrors.tuna.tsinghua.edu.cn/openwrt/releases/21.02.0-rc4/packages/aarch64_cortex-a72/luci>
src/gz openwrt_packages <https://mirrors.tuna.tsinghua.edu.cn/openwrt/releases/21.02.0-rc4/packages/aarch64_cortex-a72/packages>
src/gz openwrt_routing <https://mirrors.tuna.tsinghua.edu.cn/openwrt/releases/21.02.0-rc4/packages/aarch64_cortex-a72/routing>
src/gz openwrt_telephony <https://mirrors.tuna.tsinghua.edu.cn/openwrt/releases/21.02.0-rc4/packages/aarch64_cortex-a72/telephony>

# 扩容openwrt overlay
<https://openwrt.org/docs/guide-user/additional-software/extroot_configuration>
