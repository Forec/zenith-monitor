#coding=utf-8
__author__ = 'Forec'
import os, commands, threading
from config import UPLOAD_URL
from models import UploadThread, Basic

class Raspberry(Basic):
    def __init__(self, token, code, interval, room_temperature, work):
        Basic.__init__(self, token, code, interval, room_temperature, work)

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
        return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip()))
    @staticmethod
    def getDiskSpace():
        p = os.popen("df -h /")
        i = 0
        while 1:
            i = i +1
            line = p.readline()
            if i==2:
                stats = (line.split()[1:5])
                DISK_total = float(stats[0])
                DISK_used = float(stats[1])
                DISK_perc = float(stats[3][:-1])
                return (DISK_total, DISK_used, DISK_perc)

    def change(self):
        self.CPU_temp = Raspberry.get_cpu_temp()
        self.CPU_use = Raspberry.getCPUuse()
        self.GPU_temp = Raspberry.get_gpu_temp()
        (self.DISK_total, self.DISK_used, self.DISK_perc) = Raspberry.getDiskSpace()
        (self.RAM_total, self.RAM_used, self.RAM_free) = Raspberry.getRAMinfo()
        check = False
        if self.CPU_temp > 80 or self.CPU_use > 90 or self.GPU_temp > 70:
                # CPU 温度大于 80 度，GPU温度大于 70 度，CPU使用率大于 90%
            check = True
        if self.RAM_used / self.RAM_total > 0.9:
                # 内存大于总内存 90%
            check = True
        if self.DISK_perc > 80:
                # 硬盘使用了大于 90%
            check = True
        self.warning = check

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
