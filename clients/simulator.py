#coding=utf-8
__author__ = 'Forec'
import  urllib,  threading, json, struct, pickle
from socket import *
from models import Bulb, TV, AirConditional
from config import PORT, SERVER_IP

def buildPostData(code, status):
    return urllib.urlencode({
        'code': code,
        'status': status
    })

class WorkThread(threading.Thread):
    def __init__(self, manager, conn):
        threading.Thread.__init__(self)
        self.manager = manager
        self.conn = conn
    def __del__(self):
        if self.conn is not None:
            self.conn.close()
    def run(self):
        data = "".encode("utf-8")
        payload_size = struct.calcsize("L")
        while len(data) < payload_size:
            data += self.conn.recv(81920)
        packed_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_size)[0]
        print "消息长度", msg_size, '消息为：', data
        while len(data) < msg_size:
            data += self.conn.recv(81920)
        data= pickle.loads(data)
        do = json.loads(data)
        print "接收到远程指令：", do
        code = do.get('code')
        token = do.get('token')
        if code is None or token is None:
            return
        if manager.verify(token) == False:
            return
        if do.get('shutdown'):
            self.manager.shutdown(code)
        elif do.get('setup'):
            self.manager.setup(code)
        elif do.get('set'):
            self.manager.set(code, do.get('set'))
        return

class ListenThread(threading.Thread):
    def __init__(self, manager, port):
        threading.Thread.__init__(self)
        self.manager = manager      # 管理器
        self.setDaemon(True)
        self.sock = socket(AF_INET ,SOCK_STREAM)
        self.ADDR = ('', port)
        self.sock.bind(self.ADDR)
        self.sock.listen(100)
    def __del__(self):
        if self.sock is not None:
            self.sock.close()        
    def run(self):
        while (True):
            conn, addr = self.sock.accept()
            print addr, "接入"
            # 过滤非服务器请求
            if addr[0] != SERVER_IP:
                continue
            print "远程服务器有连接接入"
            # 启动新线程处理
            deal = WorkThread(self.manager, conn)
            deal.start()

class Manager():
    def __init__(self, token, temperature):
        self.token = token
        self.temperature = temperature
        self.deviceSet = {}
    def __del__(self):
        for device in self.deviceSet.values():
            device.shutdown()
    def insertDevice(self, device):
        if device.code is not None:
            self.deviceSet[device.code] = device
    def lookup(self, code):
        return self.deviceSet[code]
    @staticmethod
    def deviceTable():
        return {
            'Bulb': Bulb,
            'TV': TV,
            'Air': AirConditional
        }
    def shutdown(self, code):
        device = self.deviceSet.get(code)
        if device:
            device.shutdown()
    def setup(self, code):
        device = self.deviceSet.get(code)
        if device:
            device.setup()
    def set(self, code, setRequest):
        device = self.deviceSet.get(code)
        if device:
            device.set(setRequest)
    def verify(self, token):
        return self.token == token

if __name__ == '__main__':
    f = open('device.txt', 'r')
    line = f.readline().strip('\r\n').split(',')   # token, room_temperature
    manager = Manager(line[0], int(line[1]))
    while (True):
        line = f.readline()
        if line == '':
            break
        line = line.split(',')
        code = line[0]
        devicetype = line[1]
        interval = int(line[2])
        work = line[3].strip('\r\n')
        # 初始化该设备
        if work == "on":
            work = True
        else:
            work = False
        device = manager.deviceTable()[devicetype](
                manager.token,
                code,
                interval,
                manager.temperature,
                work)
        manager.insertDevice(device)
        device.start()
    listen = ListenThread(manager, PORT)
    listen.start()