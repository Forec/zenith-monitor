#coding=utf-8
__author__ = 'Forec'

import threading, urllib, urllib2, cookielib, time, json
import cv2
from encoder import NumpyEncoder
from random import randint
from config import UPLOAD_URL

def changeRange(low, high, inter1, inter2, i, rangeNum):
    if i > high:
        i += randint(-rangeNum, 0)
    elif i < low:
        i += randint(0, rangeNum)
    elif i < inter1:
        i += randint(-rangeNum, 2 * rangeNum)
    elif i > inter2:
        i += randint(-2*rangeNum, rangeNum)
    else:
        i += randint(-rangeNum, rangeNum)
    return i

class UploadThread(threading.Thread):
    def __init__(self, postdata):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.postdata = urllib.urlencode(postdata)
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
    def run(self):
        req = urllib2.Request(
            url = UPLOAD_URL,
            data = self.postdata
        )
        try:
            self.opener.open(req)
        except Exception as e:
            print "上传状态失败，错误信息:", e

class Basic(threading.Thread):
    def __init__(self, token, code, interval, room_temperature, work):
        threading.Thread.__init__(self)
        self.token = token
        self.type = 'Basic'
        self.work = work                                   # 初始根据传入参数设置
        self.warning = False                                # 初始未报警
        self.code = code                                    # 唯一识别码
        self.interval = interval                            # 每隔 interval 上报一次
        self.temperature = room_temperature                 # 基础设备温度初始为 室温
        self.room_temperature = room_temperature            # 室内温度
        self.volume = randint(180, 260)       # 180 ~ 260V
        self.initialize()
    def initialize(self):
        self.power = randint(30, 50)          # 30-50 W
        self.current = randint(300, 600)      # 3.0 ~ 6.0 A
    def setInterval(self, interval):
        self.interval = interval
    def change(self):
        if self.work == True:
            self.temperature =changeRange(self.room_temperature,
                                          80,
                                          self.room_temperature + 20,
                                          55,
                                          self.temperature,
                                          1)
                # 设备工作时波动在 -1 ~ 1 度
        else:
            tempRange = randint(-1, 5)
            if tempRange > 0:
                tempRange = 0
            self.temperature += tempRange   # 逐渐降温
            if self.temperature < self.room_temperature:
                self.temperature = self.room_temperature
            self.power = 0
            self.current = 0
    def getStatusDict(self):
        return {
                'work': self.work,
                'warning': self.warning,
                'volume': self.volume,
                'current': self.current,
                'power': self.power,
                'interval': self.interval,
                'temperature': self.temperature,
                'room': self.room_temperature
            }
    def getStatus(self):
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status': json.dumps(self.getStatusDict())
        }
    def shutdown(self):
        self.work = False
    def setup(self):
        self.work = True
        self.initialize()
    def set(self, setRequest):
        interval = setRequest.get('interval')
        try:
            if interval:
                self.interval = int(interval)
        except:
            pass
    def run(self):
        print self.type + " " + self.code + " 监控启动"
        count = 0
        while True:
            self.change()
            count += 1
            if count % self.interval == 0:
                count = 0
                status = self.getStatus()
                print self.type + " " + self.code + " 发送设备状态: ", status
                upload = UploadThread(status)
                upload.start()
            time.sleep(1)

class Bulb(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)
        self.type = 'Bulb'
        self.temperature = room_temperature    # 20-60度
        self.lightDegree = randint(1, 5)      # 1-5级灯光
        self.volume = randint(210, 220)       # 210 ~ 220V
        self.initialize()
    def initialize(self):
        self.full = randint(70, 80)          # 饱和度， 70~80%
        self.current = randint(1000, 1200)      # 10.0 ~ 12.0 A
        self.power = randint(40, 45)          # 40-45 W
    def change(self):
        Basic.change(self)
        if self.work == True:
            self.volume = changeRange(180, 250, 190, 240, self.volume, 3)    # 电压变动 -3 ~ 3 W
            self.current = changeRange(800, 1400, 900, 1300, self.current, 30)    # 电流变动 -0.3 ~ 0.3 W
            self.power = changeRange(25, 60, 30, 55, self.power, 1)    # 功率变动 -1 ~ 1 W
            self.full = changeRange(60, 100, 70, 90, self.full, 1) # 饱和度变动-1 ~ 1
        else:
            self.volume = changeRange(180, 250, 190, 240, self.volume, 3) # 电压仍然变动
            self.full = 0
        check = False
        if self.temperature > 60:               # 任何时候电灯超过 60 度报警
            check = True
        if self.volume > 240 or (self.work and self.volume < 190):
            check = True                 # 工作时电压过低/或任何时候过高
        if self.current > 1300 or (self.work and self.current < 900):
            check = True                 # 任何时候电流过高 > 1300mA
        if self.power > 55 or (self.work == True and self.power < 30) or \
                (self.work == False and self.power > 20):
            # 任何时候功率过高 或 不工作时候功率大于 20
            check = True
        self.warning = check
    def getStatus(self):
        status = Basic.getStatusDict(self)
        status['lightDegree'] = self.lightDegree
        status['full'] = self.full
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status':json.dumps(status)
        }
    def set(self, setRequest):
        Basic.set(self, setRequest)
        lightDegree = setRequest.get('lightDegree')
        full = setRequest.get('full')
        try:
            if lightDegree:
                lightDegree = int(lightDegree)
                if lightDegree < 1:
                    lightDegree = 1
                if lightDegree > 5:
                    lightDegree = 5
                self.lightDegree = lightDegree
            if full:
                full = int(full)
                if full < 0:
                    self.full = 0
                if full > 100:
                    self.full = 100
                self.full = full
        except:
            pass

class TV(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)
        self.type = 'TV'
        self.temperature = room_temperature                    # 初始时为室温
        self.volume = randint(210, 220)                         # 初始时电压 210~220V
        self.station = randint(1,1)                            # 开机位于1频道
        self.voice = randint(150, 200)                           # 音量 150 ~ 200
        self.cap = cv2.VideoCapture(str(self.station)+".mp4")   # 模拟视频
        self.image = None                                       # 当前画面
        self.initialize()
    def initialize(self):
        self.power = randint(450, 500)          # 450-500 W
        self.current = randint(1600, 1800)      # 16.0 ~ 18.0 A
    def __del__(self):
        if self.cap:
            self.cap.release()
    def change(self):
        Basic.change(self)
        if self.work == True:
            self.power = changeRange(300, 700, 350, 650, self.power, 7)    # 功率变动 -7 ~ 7 W
            self.volume = changeRange(170, 260, 190, 240, self.volume, 2)    # 电压变动 -2 ~ 2 V
            self.current = changeRange(1200, 2200, 1400, 2000, self.current, 30)   # 电流变动 -0.3V ~ 0.3V
        else:
            self.power = 0
            self.volume = changeRange(170, 260, 190, 240, self.volume, 2)    # 电压依然变动
            self.current = 0
        check = False
        if self.temperature > 50:               # 电视自身超过 50 度报警
            check = True
        if self.volume > 240 or (self.work and self.volume < 190):
            check = True                 # 工作时电压过低或任何时候电压过高
        if (self.work==True and self.current < 1400) or self.current > 2000:
            check = True                 # 工作时电流过低或任何时候电流过高
        if self.power > 650 or (self.work == True and self.power < 350) or \
                (self.work == False and self.power > 20):
            # 功率过高 或不工作时功率超过 20
            check = True
        self.warning = check
    def getStatus(self):
        status = Basic.getStatusDict(self)
        status['station'] = self.station
        status['voice'] = self.voice
        print self.name, self.code, "发送状态", status
        status['image'] = json.dumps(self.image, cls= NumpyEncoder)
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status':json.dumps(status)
        }
    def set(self, setRequest):
        Basic.set(self, setRequest)
        if self.work == False:
            return
        station = setRequest.get('station')
        voice = setRequest.get('voice')
        try:
            if station and int(station) % 2 != self.station:
                self.station = int(station) % 2
                if self.cap:
                    self.cap.release()
                self.cap = cv2.VideoCapture(str(self.station)+".mp4")
            if voice:
                voice = int(voice)
                if voice < 0:
                    voice = 0
                self.voice = voice
        except:
            pass
    # 重写播放方法，播放视频
    def run(self):
        print self.type , self.code, " 监控启动"
        count = 0
        while True:
            self.change()
            count += 1
            if count % self.interval == 0:
                count = 0
                status = self.getStatus()
                upload = UploadThread(status)
                upload.start()
                frames = 0
                if self.work:
                    if self.cap.isOpened():
                        while frames < self.interval * 24:      # 每秒24帧
                            ret, self.image = self.cap.read()
                            frames += 1
                            if ret == False:        # 读到视频结尾，循环
                                try:
                                    self.cap.release()
                                except:
                                    pass
                                try:
                                    self.cap = cv2.VideoCapture(str(self.station)+".mp4")
                                except Exception as e:
                                    print "电视切换频道错误，错误信息：", e
                         # 已经通过读取视频流来减缓时间
                else:
                    self.image = None
            time.sleep(1)

class AirConditional(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)
        self.type = 'Air'
        self.temperature = room_temperature
        self.volume = randint(210, 220)              # 初始时 210 ~ 220V
        self.level = randint(1, 5)                   # 等级
        self.mode = bool(randint(0, 1))              # True 制热
        self.speed = randint(1, 5)                   # 风速
        self.air = self.room_temperature             # 初始温度与室内相同
        self.wet = randint(30, 50)                   # 湿度维持 30 - 50 % 之间
        if self.mode == True:       # 制热
            self.target = randint(room_temperature, 35)       # 制热温度在室温上，35度下
        else:
            self.target = randint(16, room_temperature)       # 制冷温度在室温下，16度上
        self.initialize()
    def initialize(self):
        self.power = randint(900, 1100)          # 初始功率 800 ~ 1000W
        self.current = randint(1800, 2000)       # 18.0 ~ 20.0 A
    def change(self):
        Basic.change(self)
        self.wet = changeRange(30, 50, 36, 44, self.wet, 1)
        if self.work == True:
            self.power = changeRange(600, 1600, 700, 1300, self.power, 10)
                # 功率变动 -10 ~ 10 W，高于 1300或低于 700 报警
            self.volume = changeRange(170, 260, 190, 240, self.volume, 5)     # 电压变动 -5 ~ 5 V
            self.current = changeRange(800, 3000, 1200, 2600, self.current, 50)
                # 电流变动 -0.5A ~ 0.5A，高于 26A或低于12A报警
            if self.mode == True:             # 制热
                airrange = randint(-5, 1)      # 制热时随机增加温度
                if airrange < 0:
                    airrange = 0
                self.air += airrange
                if self.air > self.target:
                    self.air = self.target
                if self.air < self.room_temperature:
                    self.air = self.room_temperature
            else:
                airrange = randint(-1, 5)      # 制冷时随机降低温度
                if airrange > 0:
                    airrange = 0
                self.air += airrange
                if self.air < self.target:      # 不允许低于目标温度
                    self.air = self.target
                if self.air > self.room_temperature:
                    self.air = self.room_temperature
        else:
            self.power = 0
            self.volume = changeRange(170, 260, 190, 240, self.volume, 5)     # 电压仍然变动
            self.current = 0
            if self.mode == True:       # 制热情况下关闭，air必然比当前室温高
                airrange = randint(-1, 3)
                if airrange > 0:
                    airrange = 0
                self.air += airrange          # 室内温度逐渐增加/减小
                if self.air < self.room_temperature:
                    self.air = self.room_temperature
            else:
                airrange = randint(-3, 1)
                if airrange < 0:
                    airrange = 0
                self.air += airrange
                if self.air > self.room_temperature:
                    self.air = self.room_temperature

        check = False
        if self.temperature > 50:               # 空调自身超过 50 度报警
            check = True
        if self.volume > 240 or (self.work and self.volume < 190):
            check = True                 # 电压过低/过高
        if (self.work==True and self.current < 1200) or self.current > 2600:
            check = True                 # 电流过高或工作时电流过低
        if self.power > 1300 or (self.work == True and self.power < 700) or \
                (self.work == False and self.power > 20):
            # 功率过高 或不工作时功率超过 20
            check = True
        self.warning = check
    def getStatus(self):
        status = Basic.getStatusDict(self)
        status['speed'] = self.speed
        status['mode'] = self.mode
        status['air'] = self.air
        status['target'] = self.target
        status['level'] = self.level
        status['wet'] = self.wet
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status':json.dumps(status)
        }
    def set(self, setRequest):
        Basic.set(self, setRequest)
        mode = setRequest.get('mode')
        level = setRequest.get('level')
        speed = setRequest.get('speed')
        target = setRequest.get('target')
        try:
            if mode:
                self.mode = bool(mode)
            if level:
                level = int(level)
                if level < 1:
                    level = 1
                if level > 5:
                    level = 5
                self.level = level
            if speed:
                speed = int(speed)
                if speed < 1:
                    speed = 1
                if speed > 5:
                    speed = 5
                self.speed = speed
            if target:
                self.target = int(target)
        except:
            pass