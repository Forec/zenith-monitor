.. _dm-models:

模型介绍
==========

此部分文档主要介绍顶点云设备管理平台使用的数据库格式和模型。

.. _dm-models-database:

数据库
----------

顶点云设备管理平台默认配置使用 SQLITE ，您可以修改配置文件以选择适合您机器的数据库。顶点云设备管理平台的源码目录中提供了一个默认的 ``work.db`` 数据库文件，如果您选择使用默认配置，该文件足以满足您的需求。

顶点云设备管理平台的数据库包含 3 张基本的表，根据拓展设备的不同，继承的子表也不同：

* *cuser* ：用户模型表
* *BasicDevices* ：用户管理设备记录表
* *records* ：服务器存储设备变动记录表

.. dm-models-database-cuser:

表 cuser
>>>>>>>>>>>>

此表用于存储用户信息，表格式如下：

+---------------+-------------+---------------+--------------+-----------+-------------+-------------+
| uid           | email       | password_hash | created      | confirmed | nickname    | avatar_hash | 
+---------------+-------------+---------------+--------------+-----------+-------------+-------------+
| INTEGER       | VARCHAR(64) | VARCHAR(32)   | DATE         | BOOLEAN   | VARCHAR(64) | VARCHAR(32) |
| PRIMARY       |             |               |              |           |             |             |
| KEY           |             |               |              |           |             |             |
| AUTOINCREMENT |             |               |              |           |             |             |
+---------------+-------------+---------------+--------------+-----------+-------------+-------------+
| 用户编号      | 用户邮箱    | 用户密钥 md5  | 用户创建日期 | 是否激活  | 设备列表    | 头像链接    |
+---------------+-------------+---------------+--------------+-----------+-------------+-------------+
| about_me      | last_seen   | member_since  | token_hash   | interval  | devices     | monitor_url |
+---------------+-------------+---------------+--------------+-----------+-------------+-------------+
| VARCHAR(256)  | DATE        | DATE          | VARCHAR(32)  | INTEGER   | 外链        | VARCHAR(256)|
+---------------+-------------+---------------+--------------+-----------+-------------+-------------+
| 用户介绍      | 上次登录日期| 用户注册时间  | 用户 TOKEN   | 刷新间隔  | 一对多表    | 视频监控源  |
+---------------+-------------+---------------+--------------+-----------+-------------+-------------+

.. _dm-models-database-devices:

表 BasicDevices
>>>>>>>>>>>>>>>>>>

此表用于存储设备均具有的基本信息，表格式如下：

+-----------------+----------------+------------------+--------------+--------------+-------------+
| uid             | ownerid        | code             | path         | interval     | created     |
+-----------------+----------------+------------------+--------------+--------------+-------------+
| INTEGER         | INTEGER        | VARCHAR(12)      | VARCHAR(64)  | INTEGER      | DATE        |
| PRIMARY         |                |                  |              |              |             |
| KEY             |                |                  |              |              |             |
| AUTOINCREMENT   |                |                  |              |              |             |
+-----------------+----------------+------------------+--------------+--------------+-------------+
| 设备编号        | 资源所有者编号 | 设备唯一标识码   | 设备名称     | 设备刷新间隔 | 创建时间    |
+-----------------+----------------+------------------+--------------+--------------+-------------+
| name            | about          | temperature      | volume       | current      | power       |
+-----------------+----------------+------------------+--------------+--------------+-------------+
| VARCHAR(64)     | VARCHAR(256)   | INTEGER          | INTEGER      | INTEGER      | INTEGER     |
+-----------------+----------------+------------------+--------------+--------------+-------------+
| 设备名称        | 设备介绍       | 设备温度         | 设备电流     | 设备电流     | 设备功率    |
+-----------------+----------------+------------------+--------------+--------------+-------------+

.. _dm-models-database-records:

表 records
>>>>>>>>>>>>>

此表用于存储设备变动记录，表格式如下：

+-----------------+----------------+------------------+--------------+
| id              | device_id      | status           | created      |
+-----------------+----------------+------------------+--------------+
| INTEGER         | INTEGER        | VARCHAR(256)     | DATE         |
| PRIMARY         |                |                  |              |
| KEY             |                |                  |              |
| AUTOINCREMENT   |                |                  |              |
+-----------------+----------------+------------------+--------------+
| 变动记录编号    | 变动设备编号   | 变动信息 JSON 值 | 变动时间     |
+-----------------+----------------+------------------+--------------+


.. _dm-models-class:

内置自定义类
----------------

此部分文档主要介绍顶点云设备管理平台定义的几个模型。用户模型的定义均位于 `app/models.py` 中，包括：

* `User` ：用户类
* `Device` ：基本设备类
* `Record` ：记录类
* `AnonymousUser` ：匿名用户模型，提供给 `flask_login` 作为未登录用户实例

下面将简单介绍每个模型提供的方法。

.. _dm-models-user:

用户类
>>>>>>>>>>>>

`User` 模型同时继承了 `UserMixin` 和 SQLAlchemy 数据库模型，它具有如下元素：

.. code-block:: python

    # 用户 id
    uid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True)
    # 用户密码的加盐哈希值
    password_hash = db.Column(db.String(32))
    # 用户创建时间
    created = db.Column(db.DateTime, default = datetime.utcnow)
    # 用户是否已激活邮箱
    confirmed = db.Column(db.Boolean, default= False)
    # 用户昵称
    nickname = db.Column(db.String(64))
    # 用户头像链接
    avatar_hash = db.Column(db.String(32))
    # 用户个人介绍
    about_me = db.Column(db.Text)
    # 与 created 相同，adapter
    member_since = db.Column(db.DateTime,
                             default = datetime.utcnow)
    # 上次登录时间
    last_seen = db.Column(db.DateTime,
                          default = datetime.utcnow)
    # 用户拥有的设备，外链设备表
	devices = db.relationship('Device',
                              backref='owner',
                              lazy = 'dynamic')#,
                              #enable_typechecks=False)

`User` 类具有如下方法：

* `get_id` ：获取用户 id
* `verify_password` ：验证密码是否正确
* `generate_confirmation_token` ：生成用户邮箱验证 token
* `generate_email_change_token` ：生成修改邮箱 token
* `generate_reset_token` ：生成重置密码 token
* `generate_resetToken_token` ：生成重置 token 的 token
* `reset_password` ：用户验证重置密码的 token
* `confirm` ：用户验证邮箱激活的 token
* `reset_token` ：用户验证重置 token 函数
* `gravatar` ：获取用户头像链接，若存在自定义头像则返回自定义头像链接，否则从 gravatar 获取
* `ping` ：更新用户最近登录时间

可以看出，`User` 类的多数方法都用于处理需要鉴别用户身份的请求，包括生成 token 、验证 token 以及在验证通过后执行相应的处理。

详细方法的参数请查看 `app/models.py` ，代码中给出了详细的注释。

.. _dm-models-device:

基础设备 Device 类
>>>>>>>>>>>>>>>>>>>>>

`Device` 类是所有设备的基类，提供了如下方法：

* `setup()` ：启动设备
* `shutdown()` ：关闭设备
* `getStatus()` ：获取设备状态，DICT 格式返回
* `updateStatus(status)` ：根据参数更新设备状态
* `verify_status(jsondata)` ：根据参数判断设备是否需要更新
* `setStatus(jsondata)` ：一个闭包函数，将用户控制指令发送给远程设备


接下来请您阅读 :ref:`dm-viewfunction` 。

