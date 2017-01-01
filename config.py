# 作者：Forec
# 最后修改时间：2016-12-9
# 邮箱：forec@bupt.edu.cn
# 关于此文件: 服务器所有的配置信息在此文件中指定，具体功能由功能项后
#    的注释标明

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    TEMP_PATH = 'temp'
    CLIENT_ADDRESS = '10.201.14.176'
    CLIENT_PORT = 50002
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
                 '9d0e91f3372224b3ec7afec2' \
                 '4313e745efcf00ba4a5b767b' \
                 '35b17834d5f26efac197fd69' \
                 'd881dd92e629dbfdc2f1fbf6'         # 用于为安全操作生成 token 的密钥，不可泄露
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True            # 数据库在服务器终止时 commit 变动
    SQLALCHEMY_TRACK_MODIFICATIONS = True           # 数据库追踪改动
    ZENITH_MAIL_SUBJECT_PREFIX = '[顶点云设备管理]'         # 服务器发送验证邮件的主题前缀
    ZENITH_MAIL_SENDER = os.environ.get('ZENITH_MAIL_SENDER') or \
                         'cloud-storage@forec.cn'   # 服务器向用户发送验证邮件的邮箱
    ZENITH_RANDOM_PATH_ELEMENTS = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
                                       'h', 'i', 'j', 'k', 'l', 'm', 'n',
                                       'o', 'p', 'q', 'r', 's', 't', 'u',
                                       'v', 'w', 'x', 'y', 'z', '1', '2',
                                       '3', '4', '5', '6', '7', '8', '9',
                                       '0', 'A', 'B', 'C', 'D', 'E', 'F',
                                       'G', 'H', 'I', 'J', 'K', 'L', 'M',
                                       'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                                       'U', 'V', 'W', 'X', 'Y', 'Z']
        # 用于生成随机路径的元素
    ZENITH_VALID_THUMBNAIL = ['.jpg', '.png', '.ico', '.jpeg']
        # 允许用户使用的头像后缀名
    ZENITH_VALID_THUMBNAIL_SIZE = 512 * 1024 # 最大 512K 头像
    ZENITH_TEMPFOLDER_LENGTH = 14


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):            # 开发者环境配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'work.db')
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 25 # SSL is 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = "cloud-storage@forec.cn"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or \
                    "Cloud-Storage-2016"

class TestingConfig(Config):                # 测试环境配置
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'temp/test.sqlite')
    ZENITH_SERVER_ADDRESS = '127.0.0.1'

class WindowsConfig(Config):
    #ZENITH_SERVER_ADDRESS = '127.0.0.1'# or 'cloud.forec.cn' # 服务器部署的域名/IP地址
    #SERVER_NAME = ZENITH_SERVER_ADDRESS
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'work.db')
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 25 # SSL is 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = "cloud-storage@forec.cn"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or \
                    "Cloud-Storage-2016"

class LinuxConfig(Config):
    ZENITH_SERVER_ADDRESS = 'cloud-monitor.forec.cn' # 服务器部署的域名/IP地址
    SERVER_NAME = ZENITH_SERVER_ADDRESS
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'work.db')
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 25 # SSL is 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = "cloud-storage@forec.cn"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or \
                    "Cloud-Storage-2016"

config = {
    'basis': Config,
    'development' : DevelopmentConfig,      # 开发环境
    'linux': LinuxConfig,                   # 提供的 Linux 模板环境
    'windows': WindowsConfig,               # 提供的 Windows模板环境
    'testing' : TestingConfig,              # 测试环境
    'default' : DevelopmentConfig               # 默认为开发环境
}
