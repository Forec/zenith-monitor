.. _dm-client:

虚拟设备
============

此部分主要介绍顶点云设备管理系统用于测试的虚拟设备客户端。虚拟设备客户端位于目录 `clients` 下。

.. _dm-basic-client:

基础虚拟设备
-----------------

虚拟设备客户端的结构为

.. code-block:: shell

 - clients
   - config.py
   - encoder.py
   - models.py
   - raspberry.py
   - simulator.py
   - tvs
   - device.txt
   
其中 `config.py` 用于配置虚拟客户端和服务器交互的相关信息， `encoder.py` 是用来传输电视实时画面的编码模块， `models.py` 包含了所有虚拟设备平台提供的设备， `raspberry.py` 是一份能够监控树莓派的样例代码， `simulator.py` 包括虚拟设备管理器和模拟所需的动作。

配置
---------

`config.py` 中包括以下内容：

* `SERVER_IP` ：服务器部署的 IP 地址或域名
* `UPLOAD_URL` ：服务器预留的用于设备上传状态的入口点
* `PORT` ：虚拟客户端监听的端口，用于接收服务器发来的控制信息

编码器
-----------

* `NumpyEncoder` ：将 Numpy 中的 Array 转为 JSON 对象序列化
* `json_numpy_obj_hook` ：回调钩子

模拟器
--------------

* 类 `WorkThread` ：用于处理服务器发送的设置请求，每当服务器发送来一个请求，模拟器的监听模块会创建一个新的 `WorkThread` 来处理这个请求。
* 类 `ListenThread` ：模拟客户端的监听模块，监听 `PORT` 端口。
* 类 `Manager` ：模拟器，从 `device.txt` 中读取配置信息并创建虚拟设备。

模拟器启动过程如下：从配置文件读取用户的 Token 和室内温度，以及每个设备的编码、类型、汇报间隔和工作状态（是否开启）。

`device.txt` 的格式如下：

.. code-block:: shell

	9490544C18C15B21286685B41F825684,20
	E1A9013A447E,Bulb,5,on
	BA8120601307,Bulb,3,on
	CE683231033B,TV,3,on
	EFID2141FJKD,Air,4,on
	LI29F2MV9D7Z,Bulb,6,on
	
上面的配置文件中，第一行为用户的 Token 和室温，用逗号分隔。之后多行每行为一个设备。

每个设备需要配置四项：设备的编码（12位，用户创建设备时由服务器生成），设备类型（参考 :ref:`dm-devices` ）、设备上传状态间隔和设备的工作状态（on 或者 off）。




接下来请您阅读 :ref:`dm-ajax` 。