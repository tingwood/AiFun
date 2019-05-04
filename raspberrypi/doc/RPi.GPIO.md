# Raspberry PI GPIO基本介绍

## 树莓派GPIO引脚图
[![树莓派GPIO引脚图](http://www.elecfans.com/uploads/allimg/171206/2755779-1G2060ZP0352.png "树莓派GPIO引脚图")](http://www.elecfans.com/uploads/allimg/171206/2755779-1G2060ZP0352.png "树莓派GPIO引脚图")

## 使用RPi.GPIO
1. 安装RPi.GPIO
```pip install RPi.GPIO```
1. 导入RPi.GPIO模块。
```python
import RPi.GPIO as GPIO
```
引入之后，就可以使用GPIO模块的函数了。如果你想检查模块是否引入成功，也可以这样写：
```python
try:
    import RPi.GPIO as GPIO
except RunTImeError: 
    print（“引入错误”）
```

1. 针脚编号

在RPi.GPIO中，同时支持树莓派上的两种GPIO引脚编号。你可以使用下列代码（强制的）指定一种编号规则：
```python
#第一种编号是BOARD编号，这和树莓派电路板上的物理引脚编号相对应。使用这种编号的好处是，你的硬件将是一直可以使用的，不用担心树莓派的版本问题。因此，在电路板升级后，你不需要重写连接器或代码。
GPIO.setmode（GPIO.BOARD）
#第二种编号是BCM规则，是更底层的工作方式，它和Broadcom的片上系统中信道编号相对应。在使用一个引脚时，你需要查找信道号和物理引脚编号之间的对应规则。对于不同的树莓派版本，编写的脚本文件也可能是无法通用的。
GPIO.setmode（GPIO.BCM）
#下面代码将返回被设置的编号规则
mode = GPIO.getmode（）
```
1. 警告
如果RPi.GRIO检测到一个引脚已经被设置成了非默认值，那么你将看到一个警告信息。你可以通过下列代码禁用警告：
```python
GPIO.setwarnings（False）
```
1. 引脚设置
在使用一个引脚前，你需要设置这些引脚作为输入还是输出。配置一个引脚的代码如下：
```python
#将引脚设置为输入模式
GPIO.setup（channel， GPIO.IN）
#将引脚设置为输出模式
GPIO.setup（channel， GPIO.OUT）
#为输出的引脚设置默认值
GPIO.setup（channel， GPIO.OUT， iniTIal=GPIO.HIGH）
```
1. 释放
一般来说，程序到达最后都需要释放资源，这个好习惯可以避免偶然损坏树莓派。释放脚本中的使用的引脚：
```python
GPIO.cleanup（）
#注意 GPIO.cleanup（）只会释放掉脚本中使用的GPIO引脚，并会清除设置的引脚编号规则。
```
1. 输出
要想点亮一个LED灯，或者驱动某个设备，都需要给电流和电压他们，这个步骤也很简单，设置引脚的输出状态就可以了，代码如下：
```python
# 状态可以设置为0 / GPIO.LOW / False / 1 / GPIO.HIGH / True。如果编码规则为，GPIO.BOARD，那么channel就是对应引脚的数字。
GPIO.output（channel， state）
# 如果想一次性设置多个引脚，可使用下面的代码：
chan_list = ［11，12］
GPIO.output（chan_list， GPIO.LOW）
GPIO.output（chan_list， （GPIO.HIGH， GPIO.LOW））
#你还可以使用Input（）函数读取一个输出引脚的状态并将其作为输出值，例如：
GPIO.output（12， not GPIO.input（12））
```
1. 读取
我们也常常需要读取引脚的输入状态，获取引脚输入状态如下代码：
```python
GPIO.input（channel）
```
低电平返回0 / GPIO.LOW / False，高电平返回1 / GPIO.HIGH / True。
如果输入引脚处于悬空状态，引脚的值将是漂动的。换句话说，读取到的值是未知的，因为它并没有被连接到任何的信号上，直到按下一个按钮或开关。由于干扰的影响，输入的值可能会反复的变化。使用如下代码可以解决问题：
```python
GPIO.setup（channel， GPIO.IN， pull_up_down=GPIO.PUD_UP）
# or
GPIO.setup（channel， GPIO.IN， pull_up_down=GPIO.PUD_DOWN）
```
需要注意的是，上面的读取代码只是获取当前一瞬间的引脚输入信号。
如果需要实时监控引脚的状态变化，可以有两种办法。最简单原始的方式是每隔一段时间检查输入的信号值，这种方式被称为轮询。如果你的程序读取的时机错误，则很可能会丢失输入信号。轮询是在循环中执行的，这种方式比较占用处理器资源。另一种响应GPIO输入的方式是使用中断（边缘检测），这里的边缘是指信号从高到低的变换（下降沿）或从低到高的变换（上升沿）。

1. 轮询方式
```python
while GPIO.input（channel） == GPIO.LOW：
	  time.sleep（0.01） # wait 10 ms to give CPU chance to do other things
```

1. 中断和边检检测
边缘的定义为电信号从 LOW 到 HIGH（上升临界值）或从 HIGH 到 LOW（下降临界值）状态的改变。正常情况下，对于输入的值来说，我们更关心的是输入的状态是否发生了改变。这种状态上的改变是很重要的。
为了避免您的程序在忙于处理其它的事物时而错过了您按下按钮的操作，这里有两种方法可以解决：
wait_for_edge() 函数
event_detected() 函数
在检测到边缘时执行线程回调函数
wait_for_edge() 函数
wait_for_edge() 函数被设计用于在检测到边缘之前阻止程序的运行。换句话说，上面的示例中，等待按钮被按下的语句可以改写为：
```python
GPIO.wait_for_edge(channel, GPIO.RISING)
```
注意，您可以输入 GPIO.RISING、GPIO.FALLING、GPIO.BOTH 对边缘进行检测。这种方式的优点是占用 CPU 资源很少，因此系统可以有充裕的资源处理其它事物。
event_detected() 函数 event_detected() 函数被设计用于循环中有其它东西时使用，但不同于轮询的是，它不会错过当 CPU 忙于处理其它事物时输入状态的改变。这在类似使用 Pygame 或 PyQt 时主循环实时监听和响应 GUI 的事件是很有用的。
```python
GPIO.add_event_detect(channel, GPIO.RISING)  # 在通道上添加上升临界值检测
do_something()
if GPIO.event_detected(channel):
    print('Button pressed')
```
注意，您可以输入 GPIO.RISING、GPIO.FALLING、GPIO.BOTH 对边缘进行检测。
1. 线程回调
RPi.GPIO 在第二条线程中执行回调函数。这意味着回调函数可以同您的主程序同时运行，并且可以立即对边缘进行响应。例如：
```python
def my_callback(channel):
    print('这是一个边缘事件回调函数！')
    print('在通道 %s 上进行边缘检测'%channel)
    print('该程序与您的主程序运行在不同的进程中')
GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback)  # 在通道上添加上升临界值检测
```
... 其它程序代码 ...
如果您需要多个回调函数：
```python
def my_callback_one(channel):
    print('回调 1')
def my_callback_two(channel):
    print('回调 2')
GPIO.add_event_detect(channel, GPIO.RISING)
GPIO.add_event_callback(channel, my_callback_one)
GPIO.add_event_callback(channel, my_callback_two)
```
注意，在该示例中，回调函数为顺序运行而不是同时运行。这是因为当前只有一个进程供回调使用，而回调的运行顺序是依据它们被定义的顺序。

1. 开关防抖
您可能会注意到，每次按钮按下时，回调操作被调用不止一次。这种现象被称作“开关抖动（switch bounce）”。这里有两种方法解决开关抖动问题：
将一个 0.1uF 的电容连接到开关上。
软件防止抖动
两种方式一起用
使用软件方式抖动，可以在您指定的回调函数中添加 bouncetime= 参数。
抖动时间需要使用毫秒为单位进行书写。例如：
```python
# 在通道上添加上升临界值检测，忽略由于开关抖动引起的小于 200ms 的边缘操作
GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=200)
#or
GPIO.add_event_callback(channel, my_callback, bouncetime=200)
remove_event_detect()
```
由于某种原因，您不希望您的程序检测边缘事件，您可以将它停止：
```python
GPIO.remove_event_detect(channel)```