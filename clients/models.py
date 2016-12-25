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
        self.power = randint(30, 50)          # 30-50 W
        self.current = randint(300, 600)      # 3.0 ~ 6.0 A
        self.volume = randint(180, 260)       # 180 ~ 260V
        self.temperature = 0                                # 基础设备温度初始为 0
        self.room_temperature = room_temperature            # 室内温度
    def setInterval(self, interval):
        self.interval = interval
    def change(self):
        if self.work == True:
            self.temperature += randint(-2, 2)                  # 设备工作时波动在 -2 ~ 2 度
        else:
            self.temperature += randint(-1, 0)                  # 设备不工作时逐渐降温
            if self.temperature < self.room_temperature:
                self.temperature = self.room_temperature
    def getStatusDict(self):
        return {
                'work': self.work,
                'warning': self.warning,
                'volume': self.volume,
                'current': self.current,
                'power': self.power,
                'interval': self.interval,
                'temperature': self.temperature
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
        self.temperature = randint(20, 60)    # 20-60度
        self.lightDegree = randint(1, 5)      # 1-5级灯光
        self.full = randint(60, 100)          # 饱和度， 60~100%
        self.power = randint(30, 50)          # 30-50 W
        self.current = randint(300, 600)      # 3.0 ~ 6.0 A
        self.volume = randint(180, 260)       # 180 ~ 260V
    def change(self):
        Basic.change(self)
        if self.work == True:
            self.power += randint(-2, 2)      # 功率变动 -2 ~ 2 W
            self.volume += randint(-5, 5)     # 电压变动 -5 ~ 5 V
            self.current += randint(-30, 30)   # 电流变动 -0.3V ~ 0.3V
            self.full += randint(-2, 2)       # 饱和度变动-2 ~ 2
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
            self.power = 0
            self.volume += randint(-5, 5)       # 电压仍然变动
            self.current = 0
            self.full = 0
        check = False
        if self.temperature > 60:               # 电灯超过 60 度报警
            check = True
        if self.volume > 300 or (self.work and self.volume < 150):
            check = True                 # 电压过低/过高
        if self.current > 800:
            check = True                 # 电流过高
        if self.power > 80:                     # 功率过高
            check = True
        if self.full < 50:
            check = True                 # 饱和度过低
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
                self.lightDegree = int(lightDegree)
            if full:
                self.full = int(full)
        except:
            pass

class TV(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)
        self.type = 'TV'
        self.temperature = randint(20, 40)                      # 20-40度
        self.station = randint(1,1)                           # 1-100频道
        self.Voicevolume = randint(10, 30)                           # 音量 10-30
        self.image = None                                       # 当前画面
        self.cap = cv2.VideoCapture(str(self.station)+".mp4")   # 模拟视频 1
        self.power = randint(120, 150)          # 120-150 W
        self.current = randint(1200, 2400)      # 12.0 ~ 24.0 A
        self.volume = randint(170, 260)       # 170 ~ 260V
    def __del__(self):
        if self.cap:
            self.cap.release()
    def change(self):
        Basic.change(self)
        if self.work == True:
            self.power += randint(-2, 2)      # 功率变动 -2 ~ 2 W
            self.volume += randint(-5, 5)     # 电压变动 -5 ~ 5 V
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
            check = True                 # 电压过低/过高
        if self.current > 3000:
            check = True                 # 电流过高
        if self.power > 220:                     # 功率过高
            check = True
        self.warning = check
    def getStatus(self):
        status = Basic.getStatusDict(self)
        status['station'] = self.station
        status['voicevolume'] = self.Voicevolume
        status['image'] = json.dumps(self.image, cls= NumpyEncoder)
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status':json.dumps(status)
        }
    def set(self, setRequest):
        Basic.set(self, setRequest)
        station = setRequest.get('station')
        volume = setRequest.get('volume')
        try:
            if station and int(station) % 2 != self.station:
                self.station = int(station) % 2
                if self.cap:
                    self.cap.release()
                self.cap = cv2.VideoCapture(str(self.station)+".mp4")
            if volume:
                self.Voicevolume = int(volume)
        except:
            pass
    # 重写播放方法，播放视频
    def run(self):
        print self.type + " " + self.code + " 监控启动"
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
                            self.cap = cv2.VideoCapture(str(self.station)+".mp4")
                     # 已经通过读取视频流来减缓时间
            else:
                self.image = None
            time.sleep(self.interval)