from . import db
from .models import Device, RequestThread
from flask import json

class Bulb(Device):
    __tablename__ = 'Bulbs'

    # 与父类表相连
    uid = db.Column(db.Integer,
                    db.ForeignKey('BasicDevices.uid'),
                    primary_key=True)
    # 类型
    lightDegree = db.Column(db.String(32), default='正在获取')
    temperature = db.Column(db.String(32), default='正在获取')

    __mapper_args__ = {
       'polymorphic_identity': 'Bulb',
    }

    # 获取 JSON 格式状态
    def getStatus(self):
        return json.dumps({
            'code': self.code,
            'type': self.type,
            'work': self.work,
            'warning': self.warning,
            'interval': self.interval,
            'lightDegree': self.lightDegree,
            'temperature': self.temperature
        })

    # 更新设备信息
    def updateStatus(self, status):
        status = json.loads(status)
        work = status.get('work')
        internal = status.get('internal')
        lightDegree = status.get('lightDegree')
        temperature = status.get('temperature')
        if work is not None:
            self.work = work
        if internal is not None:
            self.interval = internal
        if lightDegree is not None:
            self.lightDegree = str(lightDegree)
        if temperature is not None:
            self.temperature = str(temperature)
        db.session.add(self)

    # 设置远程设备状态
    def setStatus(self,
                  interval = None,
                  lightDegree = None,
                  temperature = None):
        def set(interval = interval or self.interval,
                lightDegree = lightDegree or self.lightDegree,
                temperature = temperature or self.temperature):
            request = RequestThread(json.dumps({
                'code': self.code,
                'set':{
                    'interval': interval,
                    'lightDegree': lightDegree,
                    'temperature': temperature
                }
            }), self)
            request.start()
        return set(interval, lightDegree, temperature)

class PC(Device):
    type = 'PC'
    pass

class Fridge(Device):
    type = 'Fridge'
    pass

class TV(Device):
    type = 'TV'
    pass

deviceTable = {
    'PC': PC,
    'Bulb': Bulb,
    'Fridge': Fridge,
    'TV': TV
}