#coding=utf-8
__author__ = 'Forec'

import threading, urllib, urllib2, cookielib, time, json
import cv2, pickle, zlib, base64
from encoder import NumpyEncoder
from random import randint
from config import UPLOAD_URL

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
            self.temperature += randint(-2, 2)                  # 设备工作时波动在 -2 ~ 2 度
        else:
            self.temperature += randint(-1, 0)                  # 设备不工作时逐渐降温
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
        while True:
            self.change()
            status = self.getStatus()
            print self.type + " " + self.code + " 发送设备状态: ", status
            upload = UploadThread(status)
            upload.start()
            time.sleep(self.interval)

class Bulb(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)
        self.type = 'Bulb'
        self.temperature = room_temperature    # 20-60度
        self.lightDegree = randint(1, 5)      # 1-5级灯光
        self.volume = randint(15, 25)       # 15 ~ 25V
        self.initialize()
    def initialize(self):
        self.full = randint(80, 90)          # 饱和度， 60~90%
        self.current = randint(10000, 15000)      # 10.0 ~ 15.0 A
        self.power = int(self.current * self.volume / 1000)          # 30-50 W
    def change(self):
        Basic.change(self)
        if self.work == True:
            self.volume += randint(-1, 1)     # 电压变动 -1 ~ 1 V
            self.current += randint(-100, 100)   # 电流变动 -0.1A ~ 0.1A
            self.power  = int(self.volume * self.current / 1000)      # 计算功率
            self.full += randint(-1, 1)       # 饱和度变动-1 ~ 1
            if self.full > 100:
                self.full = 100
            if self.full < 0:
                self.full = 0
            if self.current < 0:
                self.current = 0
            if self.volume < 0:
                self.volume = 0
            if self.power < 0:
                self.power = 0
        else:
            self.volume += randint(-5, 5)       # 电压仍然变动
            self.full = 0
        check = False
        if self.temperature > 60:               # 任何时候电灯超过 60 度报警
            check = True
        if self.volume > 40 or (self.work and self.volume < 5):
            check = True                 # 工作时电压过低/或任何时候过高
        if self.current > 30000:
            check = True                 # 任何时候电流过高 > 30000mA
        if self.power > 80 or self.work == False and self.power > 20:
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
        self.temperature = randint(20, 40)                      # 20-40度
        self.volume = randint(170, 260)       # 170 ~ 260V
        self.station = randint(1,1)                            # 开机位于1频道
        self.voice = randint(10, 30)                           # 音量 10-30
        self.cap = cv2.VideoCapture(str(self.station)+".mp4")   # 模拟视频 1
        self.image = None                                       # 当前画面
        self.initialize()
    def initialize(self):
        self.power = randint(120, 150)          # 120-150 W
        self.current = randint(1200, 2400)      # 12.0 ~ 24.0 A
    def __del__(self):
        if self.cap:
            self.cap.release()
    def change(self):
        Basic.change(self)
        if self.work == True:
            self.power += randint(-2, 2)      # 功率变动 -2 ~ 2 W
            self.volume += randint(-3, 3)     # 电压变动 -5 ~ 5 V
            self.current += randint(-30, 30)   # 电流变动 -0.3V ~ 0.3V
            if self.current < 0:
                self.current = 0
            if self.volume < 0:
                self.volume = 0
            if self.power < 0:
                self.power = 0
        else:
            self.power = 0
            self.volume += randint(-5, 5)       # 电压仍然变动
            self.current = 0
        check = False
        if self.temperature > 50:               # 电视超过 50 度报警
            check = True
        if self.volume > 300 or (self.work and self.volume < 150):
            check = True                 # 工作时电压过低或任何时候电压过高
        if (self.work==True and self.current < 700) or self.current > 3000:
            check = True                 # 工作时电流过低或任何时候电流过高
        if self.power > 220 or (self.work == False and self.power > 20):
            # 功率过高 或不工作时功率超过 20
            check = True
        self.warning = check
    def getStatus(self):
        status = Basic.getStatusDict(self)
        status['station'] = self.station
        status['voice'] = self.voice
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
        while True:
            self.change()
            status = self.getStatus()
            print self.type + " " +self.code + " 发送设备状态: "#, status
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
            time.sleep(self.interval)

class AirConditional(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)
        self.type = 'Air'
        self.temperature = randint(20, 40)    # 20-40度
        self.volume = randint(180, 260)       # 180 ~ 260V
        self.level = randint(1, 5)            # 等级
        self.mode = bool(randint(0, 1))       # True 制热
        self.speed = randint(1, 5)            # 风速
        self.air = self.room_temperature      # 初始温度与室内相同
        if self.mode == True:       # 制热
            self.target = self.room_temperature + randint(10, 12)       # 比室温高 10 ~ 12 度
        else:
            self.target = self.room_temperature + randint(-12, -10)     # 制冷时比室温低 10 ~ 12 度
        self.initialize()
    def initialize(self):
        self.power = randint(800, 1000)          # 50-80 W
        self.current = randint(1200, 2400)      # 12.0 ~ 24.0 A
    def change(self):
        Basic.change(self)
        if self.work == True:
            self.power += randint(-2, 2)      # 功率变动 -2 ~ 2 W
            self.volume += randint(-3, 3)     # 电压变动 -5 ~ 5 V
            self.current += randint(-30, 30)   # 电流变动 -0.3V ~ 0.3V
            if self.mode == True:             # 制热
                self.air += randint(0, 1)     # 制热时增加温度
                if self.air > self.target:
                    self.air = self.target
                if self.air < self.room_temperature:
                    self.air = self.room_temperature
            else:
                self.air += randint(-1, 0)      # 制冷时降低温度
                if self.air < self.target:
                    self.air = self.target
                if self.air > self.room_temperature:
                    self.air = self.room_temperature
            if self.current < 0:
                self.current = 0
            if self.volume < 0:
                self.volume = 0
            if self.power < 0:
                self.power = 0
        else:
            self.power = 0
            self.volume += randint(-5, 5)       # 电压仍然变动
            self.current = 0
            if self.mode == True:
                self.air += randint(-1, 0)          # 室内温度逐渐增加/减小
                if self.air < self.room_temperature:
                    self.air = self.room_temperature
            else:
                self.air += randint(0, 1)
                if self.air > self.room_temperature:
                    self.air = self.room_temperature

        check = False
        if self.temperature > 50:               # 空调超过 50 度报警
            check = True
        if self.volume > 300 or (self.work and self.volume < 120):
            check = True                 # 电压过低/过高
        if (self.work==True and self.current < 700) or self.current > 3000:
            check = True                 # 电流过高或工作时电流过低
        if self.power > 1200 or (self.work == False and self.power > 20):
            # 功率过高 或不工作时功率超过 20
            check = True
        if self.air < -8:
            check = True                 # 温度过低
        if self.air > 40:
            check = True                 # 温度过高
        self.warning = check
    def getStatus(self):
        status = Basic.getStatusDict(self)
        status['speed'] = self.speed
        status['mode'] = self.mode
        status['air'] = self.air
        status['target'] = self.target
        status['level'] = self.level
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