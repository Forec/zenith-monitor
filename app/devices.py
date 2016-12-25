from . import db
from .models import Device, RequestThread, Record
from flask import json, current_app, url_for
from .encoder import json_numpy_obj_hook
import base64, pickle, os.path
import numpy, cv2
from config import basedir

class Bulb(Device):
    __tablename__ = 'Bulbs'

    # 与父类表相连
    uid = db.Column(db.Integer,
                    db.ForeignKey('BasicDevices.uid'),
                    primary_key=True)
    # 类型
    lightDegree = db.Column(db.Integer, default=-1)
    full = db.Column(db.Integer, default=-1)    # 饱和度

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
    type = 'PC'
    pass

class Fridge(Device):
    type = 'Fridge'
    pass

class TV(Device):
    __tablename__ = 'TVs'

    # 与父类表相连
    uid = db.Column(db.Integer,
                    db.ForeignKey('BasicDevices.uid'),
                    primary_key=True)
    # 类型
    station = db.Column(db.Integer, default=-1)
    Voicevolume = db.Column(db.Integer, default=-1)
    image = db.Column(db.String(32), default='')

    __mapper_args__ = {
       'polymorphic_identity': 'TV',
    }

    # 获取 JSON 格式状态
    def getStatus(self):
        status = Device.getStatus(self)
        status['station'] = self.station
        status['Voicevolume'] = self.Voicevolume,
        status['image'] = self.image
        return status

    # 更新设备信息
    def updateStatus(self, status):
        status = json.loads(status)
        Device.updateStatus(self, status)
        voiceVolume = status.get('voicevolume')
        station =status.get('station')
        image = status.get('image')
        try:
            if station is not None:
                station = int(station)
                if station < 0:
                    station = 0
                self.station = station
            if voiceVolume is not None:
                voiceVolume = int(voiceVolume)
                self.voiceVolume = voiceVolume
        except:
            return
        db.session.add(self)
        try:
            if image is not None:
                image = json.loads(image, object_hook=json_numpy_obj_hook)
            # try:
            #     os.remove(os.path.join(basedir,
            #                            'app/static/tvs/' +
            #                            self.image + '.png'))
            # except:
            #     pass
            self.image = self.randomCode()
            store_path = os.path.join(basedir,
                                 'app/static/tvs/' +
                                    self.image + '.png')
            cv2.imwrite(store_path, image)
        except Exception as e:
            print(e)
        r = Record(device = self,
                   status = json.dumps(self.getStatus()))
        db.session.add(r)

    # 设置远程设备状态
    def setStatus(self, jsondata):
        def set(interval = jsondata.get('interval') or self.interval,
                station = jsondata.get('station') or self.station,
                volume = jsondata.get('volume') or self.volume):
            request = RequestThread(json.dumps({
                'code': self.code,
                'token': self.owner.token_hash,
                'set':{
                    'interval': interval,
                    'station': station,
                    'volume': volume
                }
            }), self)
            request.start()
        return set()

deviceTable = {
    'PC': PC,
    'Bulb': Bulb,
    'Fridge': Fridge,
    'TV': TV
}

deviceNumbers = {
    1: 'PC',
    2: 'Bulb',
    3: 'Fridge',
    4: 'TV'
}