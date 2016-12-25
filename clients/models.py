#coding=utf-8
__author__ = 'Forec'

import threading, urllib, urllib2, cookielib, time, json
import cv2
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
    def getStatus(self):
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status': json.dumps({
                'work': self.work,
                'warning': self.warning,
                'interval': self.interval,
                'temperature': self.temperature
            })
        }
    def shutdown(self):
        self.work = False
    def setup(self):
        self.work = True
    def set(self, setRequest):
        interval = setRequest.get('interval')
        if interval:
            self.interval = int(interval)
    def run(self):
        print self.type + " " + self.code + " 启动"
        while True:
            self.change()
            if self.work:
                # 设备正在运行
                status = self.getStatus()
                print self.type + " 发送设备状态: ", status
                upload = UploadThread(status)
                upload.start()
            time.sleep(self.interval)

class Bulb(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)
        self.type = 'Bulb'
        self.temperature = randint(20, 60)    # 20-60度
        self.lightDegree = randint(1, 5)      # 1-5级灯光
    def change(self):
        if self.temperature > 60:               # 电灯超过 60 度报警
            self.warning = True
    def getStatus(self):
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status':json.dumps({
                'work': self.work,
                'interval': self.interval,
                'lightDegree': self.lightDegree,
                'temperature': self.temperature
            })
        }
    def set(self, setRequest):
        super.set(self, setRequest)
        lightDegree = setRequest.get('lightDegree')
        if lightDegree:
            self.lightDegree = int(lightDegree)

class TV(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)
        self.type = 'TV'
        self.temperature = randint(20, 40)                      # 20-40度
        self.station = randint(1, 10)                           # 1-100频道
        self.volume = randint(10, 30)                           # 音量 10-30
        self.image = None                                       # 当前画面
        self.cap = cv2.VideoCapture(str(self.station)+".mp4")   # 模拟视频 1
    def __del__(self):
        if self.cap:
            self.cap.release()
    def change(self):
        if self.temperature > 50:                               # 电视高于 50 度报警
            self.warning = True
    def getStatus(self):
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status':json.dumps({
                'work': self.work,
                'interval': self.interval,
                'station': self.station,
                'volume': self.volume,
                'temperature': self.temperature,
                'image': self.image
            })
        }
    def set(self, setRequest):
        super.set(self, setRequest)
        station = setRequest.get('station')
        volume = setRequest.get('volume')
        if station:
            self.station = int(station) % 2
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(str(self.station)+".mp4")
        if volume:
            self.volume = int(volume)
    # 重写播放方法，播放视频
    def run(self):
        print self.type + " " + self.code + " 启动"
        while True:
            self.change()
            if self.work:
                # 设备正在运行
                status = self.getStatus()
                print self.type + " 发送设备状态: ", status
                upload = UploadThread(status)
                upload.start()
                frames = 0
                if self.cap.isOpened():
                    while frames < self.interval * 24:      # 每秒24帧
                        ret, self.image = self.cap.read()
                        frames += 1
                    continue    # 已经通过读取视频流来减缓时间
            time.sleep(self.interval)