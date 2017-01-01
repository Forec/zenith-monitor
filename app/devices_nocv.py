from . import db
from .models import Device, RequestThread, Record
from flask import json

class Bulb(Device):
    __tablename__ = 'Bulbs'

    # 与父类表相连
    uid = db.Column(db.Integer,
                    db.ForeignKey('BasicDevices.uid'),
                    primary_key=True)
    # 类型
    lightDegree = db.Column(db.Integer, default=0)
    full = db.Column(db.Integer, default=0)    # 饱和度

    __mapper_args__ = {
       'polymorphic_identity': 'Bulb',
    }

    # 获取 JSON 格式状态
    def getStatus(self):
        status = Device.getStatus(self)
        status['full'] = self.full
        status['lightDegree'] = self.lightDegree
        return status

    # 更新设备信息
    def updateStatus(self, status):
        status = json.loads(status)
        Device.updateStatus(self,status)
        lightDegree = status.get('lightDegree')
        full = status.get('full')
        try:
            if lightDegree is not None:
                lightDegree = int(lightDegree)
                if lightDegree < 0:
                    lightDegree = 0
                self.lightDegree = lightDegree
            if full is not None:
                full = int(full)
                if full < 0:
                    full = 0
                if full > 100:
                    full = 100
                self.full = full
        except:
            return
        db.session.add(Record(device = self,
                   status = json.dumps(self.getStatus())))
        db.session.add(self)

    def verify_status(self, jsondata):
        lightDegree = jsondata.get('lightDegree')
        full = jsondata.get('full')
        same = Device.verify_status(self, jsondata)
        try:
            if lightDegree is not None:
                lightDegree = int(lightDegree)
            if full is not None:
                full = int(full)
        except:
            return None
        if lightDegree is not None and lightDegree != self.lightDegree:
            self.lightDegree = lightDegree
            same = False
        if full is not None and full != self.full:
            self.full = full
            same = False
        if same == False:
            db.session.add(self)
            return self.getStatus()
        return None

    # 设置远程设备状态
    def setStatus(self, jsondata):
        def set(interval = jsondata.get('interval') or self.interval,
                lightDegree = jsondata.get('lightDegree') or self.lightDegree,
                full = jsondata.get('full') or self.full):
            request = RequestThread(json.dumps({
                'code': self.code,
                'token': self.owner.token_hash,
                'set':{
                    'interval': interval,
                    'lightDegree': lightDegree,
                    'full': full
                }
            }), self)
            request.start()
        return set()

class PC(Device):
    __tablename__ = 'PCs'

    # 与父类表相连
    uid = db.Column(db.Integer,
                    db.ForeignKey('BasicDevices.uid'),
                    primary_key=True)
    # 类型
    cpu_use = db.Column(db.Float, default=0)
    cpu_temp = db.Column(db.Float, default=0)
    gpu_temp = db.Column(db.Float, default=0)
    disk_total = db.Column(db.String(12), default='')    # GB
    disk_used = db.Column(db.String(12), default ='')
    disk_perc = db.Column(db.Float, default=0)
    ram_total = db.Column(db.Float, default=0) # MB
    ram_used = db.Column(db.Float, default=0)
    ram_free = db.Column(db.Float, default=0)

    __mapper_args__ = {
       'polymorphic_identity': 'PC',
    }

    # 获取 JSON 格式状态
    def getStatus(self):
        return {
            'code': self.code,
            'type': self.type,
            'name': self.name,
            'interval': self.interval,
            'last_seen': self.last_seen,
            'work': self.work,
            'warning': self.warning,
            'cpu_temp': self.cpu_temp,
            'gpu_temp': self.gpu_temp,
            'cpu_use': self.cpu_use,
            'disk_total': self.disk_total,
            'disk_used': self.disk_used,
            'disk_perc': self.disk_perc,
            'ram_total': self.ram_total,
            'ram_used': self.ram_used,
            'ram_free': self.ram_free,
            'interval': self.interval
        }

    # 更新设备信息
    def updateStatus(self, status):
        status = json.loads(status)
        Device.updateStatus(self,status)
        ram_total = status.get('ram_total')
        ram_used = status.get('ram_used')
        ram_free = status.get('ram_free')
        disk_total = status.get('disk_total')
        disk_used = status.get('disk_used')
        disk_perc = status.get('disk_perc')
        cpu_use = status.get('cpu_use')
        cpu_temp = status.get('cpu_temp')
        gpu_temp = status.get('gpu_temp')

        try:
            if ram_total is not None:
                ram_total = float(ram_total)
                if ram_total < 0:
                    ram_total = 0
                self.ram_total = ram_total
            if ram_used is not None:
                ram_used = float(ram_used)
                if ram_used < 0:
                    ram_used = 0
                self.ram_used = ram_used
            if ram_free is not None:
                ram_free = float(ram_free)
                if ram_free < 0:
                    ram_free = 0
                self.ram_free = ram_free
            if disk_total is not None:
                self.disk_total = disk_total
            if disk_used is not None:
                self.disk_used = disk_used
            if disk_perc is not None:
                disk_perc = float(disk_perc)
                if disk_perc < 0:
                    disk_perc = 0
                self.disk_perc = disk_perc
            if cpu_temp is not None:
                cpu_temp = float(cpu_temp)
                self.cpu_temp = cpu_temp
            if gpu_temp is not None:
                gpu_temp = float(gpu_temp)
                self.gpu_temp = gpu_temp
            if cpu_use is not None:
                cpu_use = float(cpu_use)
                self.cpu_use = cpu_use
        except:
            return
        db.session.add(Record(device = self,
                   status = json.dumps(self.getStatus())))
        db.session.add(self)

    def verify_status(self, jsondata):
        return None

    # 设置远程设备状态
    def setStatus(self, jsondata):
        pass

class AirCondition(Device):
    __tablename__ = 'Airs'

    # 与父类表相连
    uid = db.Column(db.Integer,
                    db.ForeignKey('BasicDevices.uid'),
                    primary_key=True)
    # 类型
    level = db.Column(db.Integer, default=0)    # 功效等级
    speed = db.Column(db.Integer, default=0)    # 风速
    mode = db.Column(db.Boolean, default=0)    # 模式
    target = db.Column(db.Integer, default=0)  # 目标温度
    air = db.Column(db.Integer, default=0)     # 空调管辖范围内温度
    wet = db.Column(db.Integer, default=0)      # 湿度

    __mapper_args__ = {
       'polymorphic_identity': 'Air',
    }

    # 获取 JSON 格式状态
    def getStatus(self):
        status = Device.getStatus(self)
        status['level'] = self.level
        status['speed'] = self.speed
        status['mode'] = self.mode
        status['target'] = self.target
        status['air'] = self.air
        status['wet'] = self.wet
        return status

    # 更新设备信息
    def updateStatus(self, status):
        status = json.loads(status)
        Device.updateStatus(self,status)
        speed = status.get('speed')
        target = status.get('target')
        mode = status.get('mode')
        air = status.get('air')
        level = status.get('level')
        wet = status.get('wet')
        try:
            if level is not None:
                level = int(level)
                if level < 0:
                    level = 0
                if level > 5:
                    level = 5
                self.level = level
            if wet is not None:
                wet = int(wet)
                if wet < 0:
                    level = 0
                if wet > 100:
                    wet = 100
                self.level = level
            if speed is not None:
                speed = int(speed)
                if speed < 0:
                    speed = 0
                if speed > 5:
                    speed = 5
                self.speed = speed
            if target is not None:
                target = int(target)
                self.target = target
            if mode is not None:
                mode = bool(mode)
                self.mode = mode
            if air is not None:
                air = int(air)
                self.air = air
        except:
            return
        db.session.add(Record(device = self,
                   status = json.dumps(self.getStatus())))
        db.session.add(self)

    def verify_status(self, jsondata):
        level = jsondata.get('level')
        target = jsondata.get('target')
        speed = jsondata.get('speed')
        mode = jsondata.get('mode')
        wet = jsondata.get('wet')
        same = Device.verify_status(self, jsondata)
        try:
            if level is not None:
                level = int(level)
            if wet is not None:
                wet = int(wet)
            if mode is not None:
                mode = bool(mode)
            if target is not None:
                target = int(target)
            if speed is not None:
                speed = int(speed)
        except:
            return None
        if level is not None and level != self.level:
            self.level = level
            same = False
        if wet is not None and wet != self.wet:
            self.wet = wet
            same = False
        if mode is not None and mode != self.mode:
            self.mode = mode
            same = False
        if target is not None and target != self.target:
            self.target = target
            same = False
        if speed is not None and speed != self.speed:
            self.speed = speed
            same = False
        if same == False:
            db.session.add(self)
            return self.getStatus()
        return None

    # 设置远程设备状态
    def setStatus(self, jsondata):
        def set(interval = jsondata.get('interval') or self.interval,
                level = jsondata.get('level') or self.level,
                mode = jsondata.get('mode') or self.mode,
                air = jsondata.get('air') or self.air,
                target = jsondata.get('target') or self.target,
                speed = jsondata.get('speed') or self.speed,
                wet = jsondata.get('wet') or self.wet):
            request = RequestThread(json.dumps({
                'code': self.code,
                'token': self.owner.token_hash,
                'set':{
                    'interval': interval,
                    'speed': speed,
                    'level': level,
                    'target': target,
                    'air': air,
                    'mode': mode,
                    'wet': wet
                }
            }), self)
            request.start()
        return set()

class TV(Device):
    __tablename__ = 'TVs'

    # 与父类表相连
    uid = db.Column(db.Integer,
                    db.ForeignKey('BasicDevices.uid'),
                    primary_key=True)
    # 类型
    station = db.Column(db.Integer, default=-1)
    voice = db.Column(db.Integer, default=-1)
    image = db.Column(db.String(32), default='')
    preimage = db.Column(db.String(32), default ='')

    __mapper_args__ = {
       'polymorphic_identity': 'TV',
    }

    # 获取 JSON 格式状态
    def getStatus(self):
        status = Device.getStatus(self)
        status['station'] = self.station
        status['voice'] = self.voice
        status['image'] = self.image
        return status

    # 更新设备信息
    def updateStatus(self, status):
        status = json.loads(status)
        Device.updateStatus(self, status)
        voice = status.get('voice')
        station =status.get('station')
        image = status.get('image')
        try:
            if station is not None:
                station = int(station)
                if station < 0:
                    station = 0
                self.station = station
            if voice is not None:
                voice = int(voice)
                self.voice = voice
        except Exception as e:
            return
        db.session.add(self)
        r = Record(device = self,
                   status = json.dumps(self.getStatus()))
        db.session.add(r)

    def verify_status(self, jsondata):
        station = jsondata.get('station')
        voice = jsondata.get('voice')
        same = Device.verify_status(self, jsondata)
        try:
            if station is not None:
                station = int(station)
            if voice is not None:
                voice = int(voice)
        except:
            return None
        if station is not None and station != self.station:
            self.station = station
            same = False
        if voice is not None and voice != self.voice:
            self.voice = voice
            same = False
        if same == False:
            db.session.add(self)
            return self.getStatus()
        return None

    # 设置远程设备状态
    def setStatus(self, jsondata):
        def set(interval = jsondata.get('interval') or self.interval,
                station = jsondata.get('station') or self.station,
                voice = jsondata.get('voice') or self.voice):
            request = RequestThread(json.dumps({
                'code': self.code,
                'token': self.owner.token_hash,
                'set':{
                    'interval': interval,
                    'station': station,
                    'voice': voice
                }
            }), self)
            request.start()
        return set()

deviceTable = {
    'PC': PC,
    'Bulb': Bulb,
    'Air': AirCondition,
    'TV': TV
}

deviceNumbers = {
    1: 'PC',
    2: 'Bulb',
    3: 'Air',
    4: 'TV'
}