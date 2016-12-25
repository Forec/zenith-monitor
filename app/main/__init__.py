# 作者：Forec
# 最后修改时间：2016-12-20
# 邮箱：forec@bupt.edu.cn
# 关于此文件：初始化 main 蓝本

from flask import Blueprint

# 注册蓝本
main = Blueprint('main', __name__)

from . import views, errors
