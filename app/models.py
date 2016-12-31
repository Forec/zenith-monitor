# 作者：Forec
# 最后修改时间：2016-12-24
# 邮箱：forec@bupt.edu.cn
# 关于此文件：应用涉及的全部模型，包括用户、设备

import hashlib, threading, struct, os, json, pickle, time, calendar
from random import randint
from math import ceil
from socket import *
from datetime import datetime
from config import basedir
from flask import current_app, request
from flask import url_for, jsonify
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer
from . import db, login_manager

# -------------------------------------------------------------------------
# 设备历史信息记录
class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key = True)
    device_id = db.Column(db.Integer,
                          db.ForeignKey('BasicDevices.uid'))
    status = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime,
                          default=datetime.utcnow)

# -------------------------------------------------------------------------
# 请求线程
class RequestThread(threading.Thread):
    def __init__(self, data, device):
        threading.Thread.__init__(self)
        self.sock = socket(AF_INET ,SOCK_STREAM)
        self.ADDR = (current_app.config['CLIENT_ADDRESS'],
                     current_app.config['CLIENT_PORT'])
        self.data = pickle.dumps(data, protocol=2)
        self.device = device
    def __del__(self):
        if self.sock:
            self.sock.close()
    def run(self):
        try:
            self.sock.connect(self.ADDR)
            self.sock.sendall(struct.pack("L", len(self.data)) + self.data)
        except Exception as e:
            print("控制线程发送失败，错误：", e)
            return

# -------------------------------------------------------------------------
# 设备模型
class Device(db.Model):
    __tablename__ = 'BasicDevices'
    # 类型
    type = db.Column(db.String(32))

    uid = db.Column(db.Integer, primary_key=True)
    # 设备所有者
    ownerid = db.Column(db.Integer,
                        db.ForeignKey('cuser.uid'))
    # 设备名称
    name = db.Column(db.String(64), default='设备名称未指定')
    # 识别码，默认为随机数 + 创建时刻的 md5 值
    code = db.Column(db.String(12), unique = True)
    # 监控间隔
    interval = db.Column(db.Integer, default = 60)
    # 设备介绍
    about = db.Column(db.String(256), default='')
    # 设备温度
    temperature = db.Column(db.String(32), default='正在获取')
    # 历史记录
    records = db.relationship('Record',
                              backref='device',
                              lazy = 'dynamic')
    # 创建时间
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def randomCode(self):
        return hashlib.md5((str(self.name)+ str(self.ownerid) +
                         str(datetime.utcnow())).encode('utf-8')).\
                         hexdigest().upper()[:12]

    # 与子类映射关系
    __mapper_args__ = {
        'polymorphic_identity':'Basic',
        'polymorphic_on':type
    }

    # 是否开启
    work = db.Column(db.Boolean, default=False)
    # 是否报警
    warning = db.Column(db.Boolean, default=False)
    volume = db.Column(db.Integer, default=-1)    # 电压
    current = db.Column(db.Integer, default = -1) # 电流
    power = db.Column(db.Integer, default=-1)     # 功率
    room = db.Column(db.Integer, default=-1)      # 室温
    last_seen = db.Column(db.Integer,
        default=int(calendar.timegm(datetime.utcnow().utctimetuple())))

    def __repr__(self):
        return '<Device %r>' % self.name

    # 启动设备
    def setup(self):
        request = RequestThread(json.dumps({
            'code': self.code,
            'token': self.owner.token_hash,
            'setup': 1
        }), self)
        request.start()

    # 关闭设备
    def shutdown(self):
        request = RequestThread(json.dumps({
            'code': self.code,
            'token': self.owner.token_hash,
            'shutdown': 1
        }), self)
        request.start()

    # 获取 JSON 格式状态
    def getStatus(self):
        statusJSON = {
            'code': self.code,
            'type': self.type,
            'work': self.work,
            'name': self.name,
            'volume': self.volume,
            'current': self.current,
            'power': self.power,
            'warning': self.warning,
            'interval': self.interval,
            'temperature': self.temperature,
            'room': self.room,
            'last_seen': self.last_seen
        }
        return statusJSON

    # 更新设备状态
    def updateStatus(self, status):
        work = status.get('work')
        warning = status.get('warning')
        volume = status.get('volume')
        current = status.get('current')
        power = status.get('power')
        interval = status.get('interval')
        temperature = status.get('temperature')
        room = status.get('room')
        try:
            if work is not None:
                work = bool(work)
                self.work = work
            if warning is not None:
                warning = bool(warning)
                self.warning = warning
            if interval is not None:
                internal = int(interval)
                if internal < 1:
                    internal = 1
                self.interval = internal
            if temperature is not None:
                int(temperature)
                self.temperature = temperature
            if volume is not None:
                int(volume)
                self.volume = volume
            if current is not None:
                int(current)
                self.current = current
            if power is not None:
                int(power)
                self.power = power
            if room is not None:
                int(room)
                self.room = room
        except:
            return
        self.last_seen = int(calendar.timegm(datetime.utcnow().utctimetuple()))  # 更新上次时间

    def verify_status(self, jsondata):
        interval = jsondata.get('interval')
        try:
            if interval is not None:
                interval = int(interval)
        except:
            return True
        print(interval, self.interval)
        if interval is not None:
            if interval != self.interval:
                self.interval = interval
                return False
        return True

    # 设置远程设备状态
    def setStatus(self, jsondata):
        def set(interval = jsondata.get('interval') or self.interval):
            request = RequestThread(json.dumps({
                'code': self.code,
                'token': self.owner.token_hash,
                'set':{
                    'interval': interval
                }
            }), self)
            request.start()
        return set()

# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'cuser'
    # 用户 id
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True)
    # 用户密码的加盐哈希值
    password_hash = db.Column(db.String(32))
    # 用户设备 token 值
    token_hash = db.Column(db.String(32), unique=True, default =
                         hashlib.md5((str(randint(1, 9999999999)) +
                         str(datetime.utcnow())).encode('utf-8')).\
                         hexdigest().upper())

    # 用户是否已激活邮箱
    confirmed = db.Column(db.Boolean, default= False)
    # 用户昵称
    nickname = db.Column(db.String(64))
    # 用户个人介绍
    about_me = db.Column(db.Text)
    # 用户头像链接
    avatar_hash = db.Column(db.String(32))
    # 用户创建时间
    member_since = db.Column(db.DateTime,
                             default = datetime.utcnow)
    # 上次登录时间
    last_seen = db.Column(db.DateTime,
                          default = datetime.utcnow)
    # 刷新间隔
    interval = db.Column(db.Integer, default=2)

    # 用户拥有的设备，外链 Device 表
    devices = db.relationship('Device',
                              backref='owner',
                              lazy = 'dynamic')#,
                              #enable_typechecks=False)

    # 获取用户 id
    def get_id(self):
        return self.uid

    # 设定无法从模型中获取密码
    @property
    def password(self):
        raise AttributeError('密码项不能被获取')
    # 设定密码自动转为哈希值
    @password.setter
    def password(self, _password):
        self.password_hash = hashlib.md5(_password.encode('utf-8')).\
            hexdigest().upper()
    # 密码验证函数
    def verify_password(self, _password):
        return self.password_hash == hashlib.md5(_password.encode('utf-8')).\
            hexdigest().upper()
    # 设备 token 验证函数
    def verify_token(self, _token):
        return self.token_hash == _token

    # 生成重置 token 的 token
    def generate_resetToken_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'],
                expiration)
        return s.dumps({'confirm':self.uid,
                        'old': self.token_hash})
    # 用户重置 token
    def reset_token(self, token):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.uid or \
            data.get('old') != self.token_hash:
            return False
        self.token_hash = hashlib.md5((str(randint(1, 9999999999)) +
                         str(datetime.utcnow())).encode('utf-8')).\
                         hexdigest().upper()
        db.session.add(self)
        db.session.commit()
        return True

    # 生成邮箱验证 token
    def generate_confirmation_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'],
                expiration)
        return s.dumps({'confirm':self.uid})
    # 生成修改邮箱 token
    def generate_email_change_token(self, new_email, expiration = 3600):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'],
                expiration)
        return s.dumps({'change_email': self.uid,
                        'new_email': new_email})
    # 生成重置密码 token
    def generate_reset_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'],
                expiration)
        return s.dumps({'reset': self.uid})
    # 生成删除设备 token
    def generate_delete_token(self, deviceid, expiration):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'],
                expiration)
        return s.dumps({'delete': deviceid,
                        'user':self.uid})

    # 用户验证重置密码的 token
    def reset_password(self, token ,new_password):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.uid:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    # 用户验证邮箱激活的 token
    def confirm(self, token):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.uid:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    # 用户验证修改邮箱的 token
    def change_email(self, token):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.uid:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email = new_email).first() is not None:
            return False
        self.email = new_email
        if self.avatar_hash is None or \
            self.avatar_hash[0] != ':':
            # 用户无自定义头像则重新生成 avatar hash
            self.avatar_hash = hashlib.md5(
                    new_email.encode('utf-8')).\
                    hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    # 用户验证删除设备的 token
    def delete_device(self, token):
        s = TimedJSONWebSignatureSerializer(
                current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        if data.get('delete') is None:
            return None
        if data.get('user') is None:
            return None
        user = User.query.filter_by(uid=data.get('user')).first()
        if user.uid != self.uid:
            return None
        # 获取要删除的 device 编号
        deviceid = data.get('delete')
        device = Device.query.filter_by(uid=deviceid).first()
        if device is None or device.ownerid != self.uid:
            return None
        db.session.delete(device)
        db.session.commit()
        return True

    # 获取用户头像链接
    def gravatar(self, size=100, default='identicon', rating='g'):
        # 若存在用户自定义头像则返回自定义头像
        if self.avatar_hash is not None and self.avatar_hash[0] == ':':
            # 定义 avatar_hash 的第一个字符为 : 时有自定义头像
            return self.avatar_hash[1:]
        for _suffix in current_app.config['ZENITH_VALID_THUMBNAIL']:
            thumbnailPath = os.path.join(basedir,
                                 'app/static/thumbnail/' +
                                    str(self.uid) + _suffix)
            if os.path.isfile(thumbnailPath):
                thumbnailURL = url_for('static',
                               filename = 'thumbnail/' +
                                          str(self.uid) +
                                          _suffix,
                               _external=True)
                self.avatar_hash = ':'+ thumbnailURL
                db.session.add(self)
                return thumbnailURL

        # 不存在自定义头像则从 gravatar 获取
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url= 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or \
               hashlib.md5(self.email.encode('utf-8')).\
               hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                url = url,
                hash = hash,
                size=size,
                default = default,
                rating = rating
        )

    # 更新用户最近登录时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # 生成随机用户
    @staticmethod
    def generate_fake(count=5):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     nickname = forgery_py.internet.user_name(True),
                     password = forgery_py.lorem_ipsum.word(),
                     confirmed = True,
                     member_since = forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    # 用户初始化函数
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # 为用户分配头像链接
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')
            ).hexdigest()
        # 新加入的用户需关注自己

# --------------------------------------------------------------------
# 匿名用户模型，注册到 flask_login 为未登录用户
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

# 注册匿名用户
login_manager.anonymous_user = AnonymousUser
login_manager.login_message = u"您需要先登录才能访问此界面！"

# ----------------------------------------------------------------------
# flask_login 所需的用户登录标识符
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# -----------------------------------------------------------------------
# 自定义内容分页模型
class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
    # 页数
    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))
    # 当前页是否有更前页
    @property
    def has_prev(self):
        return self.page > 1
    # 当前页是否有后页
    @property
    def has_next(self):
        return self.page < self.pages
    # 当前页的内容列表
    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
