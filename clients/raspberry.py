#coding=utf-8
__author__ = 'Forec'
import os, commands, threading, time
import urllib, urllib2, cookielib, json

SERVER_IP = '10.8.183.152'#'10.201.14.176'
TOKEN = '9490544C18C15B21286685B41F825684'
CODE = 'JFIDEO2193FJ'
UPLOAD_URL = 'http://' + SERVER_IP + ':5000/upload_status/'

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


class Raspberry(threading.Thread):
    def __init__(self, token, code, interval, room_temperature, work):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.work = work
        self.warning = False
        self.code = code
        self.token = token
        self.room_temperature = room_temperature
        self.interval = interval

        self.type = 'PC'

        self.CPU_temp = -1  # float
        self.CPU_use = -1   # float
        self.GPU_temp = -1  # float

        self.RAM_total = -1
        self.RAM_used = -1
        self.RAM_free = -1

        self.DISK_total = -1
        self.DISK_used = -1
        self.DISK_perc = -1

    def setInterval(self, interval):
        self.interval = interval

    @staticmethod
    def get_cpu_temp():
        tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
        cpu_temp = tempFile.read()
        tempFile.close()
        return float(cpu_temp)/1000
    @staticmethod
    def get_gpu_temp():
        gpu_temp = commands.getoutput( '/opt/vc/bin/vcgencmd measure_temp' ).\
            replace( 'temp=', '' ).replace( '\'C', '' )
        return float(gpu_temp)
    @staticmethod
    def getRAMinfo():
        p = os.popen('free')
        i = 0
        while 1:
            i = i + 1
            line = p.readline()
            if i==2:
                stats = (line.split()[1:4])
                RAM_total = round(int(stats[0]) / 1000,1)
                RAM_used = round(int(stats[1]) / 1000,1)
                RAM_free = round(int(stats[2]) / 1000,1)
                return (RAM_total, RAM_used, RAM_free)
    @staticmethod
    def getCPUuse():
        return(float(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip())))
    @staticmethod
    def getDiskSpace():
        p = os.popen("df -h /")
        i = 0
        while 1:
            i = i +1
            line = p.readline()
            if i==2:
                stats = (line.split()[1:5])
                DISK_total = stats[0]
                DISK_used = stats[1]
                DISK_perc = float(stats[3][:-1])
                return (DISK_total, DISK_used, DISK_perc)

    def change(self):
        self.CPU_temp = Raspberry.get_cpu_temp()
        self.CPU_use = Raspberry.getCPUuse()
        self.GPU_temp = Raspberry.get_gpu_temp()
        (self.DISK_total, self.DISK_used, self.DISK_perc) = Raspberry.getDiskSpace()
        (self.RAM_total, self.RAM_used, self.RAM_free) = Raspberry.getRAMinfo()
        check = False
        if self.CPU_temp > 80 or self.CPU_use > 90 or self.GPU_temp > 80:
            print('TEMP is too large:', self.CPU_temp, self.CPU_use, self.GPU_temp)
            print(self.CPU_temp > 80)
            print(self.GPU_temp > 80)
            print(self.CPU_use > 90)
                # CPU 温度大于 80 度，GPU温度大于 80 度，CPU使用率大于 90%
            check = True
        if self.RAM_used / self.RAM_total > 0.9:
            print('RAM used is too large:', self.RAM_used, self.RAM_total, self.RAM_used/self.RAM_total)
                # 内存大于总内存 90%
            check = True
        if self.DISK_perc > 80:
            print('disk is too large:', self.DISK_perc)
                # 硬盘使用了大于 90%
            check = True
        self.warning = check

    def getStatusDict(self):
        return {
                'work': self.work,
                'warning': self.warning,
                'cpu_temp': self.CPU_temp,
                'gpu_temp': self.GPU_temp,
                'cpu_use': self.CPU_use,
                'disk_total': self.DISK_total,
                'disk_used': self.DISK_used,
                'disk_perc': self.DISK_perc,
                'ram_total': self.RAM_total,
                'ram_used': self.RAM_used,
                'ram_free': self.RAM_free,
                'interval': self.interval
            }

    def getStatus(self):
        return {
            'token': self.token,
            'code': self.code,
            'type': self.type,
            'status': json.dumps(self.getStatusDict())
        }

    def run(self):
        print self.type + " " + self.code + " 监控启动"
        while True:
            self.change()
            status = self.getStatus()
            print self.type + " " + self.code + " 发送设备状态: ", status
            upload = UploadThread(status)
            upload.start()
            time.sleep(self.interval)

if __name__ == '__main__':
    r = Raspberry(TOKEN,
                  CODE,
                  3,
                  23,
                  True)
    r.start()
    while True:
        time.sleep(10)