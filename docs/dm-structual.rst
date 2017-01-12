.. _dm-structual:

框架分析
===========

此部分文档主要介绍顶点云设备管理平台的框架结构。

顶点云设备管理平台源码文件结构如下：

.. code-block:: shell

 - zenith-monitor
   - app
     - auth
     - main
     - static
       - thumbnail
     - templates
     - ...
	 - devices.py
     - models.py
   - settings
   - config.py
   - manage.py
   - work.db
		
以上几个目录对应的功能如下：

* *auth* ：对应 :ref:`dm-blueprint-auth` ，用于处理用户注册、登录等需要特权的请求。
* *main* ：对应 :ref:`dm-blueprint-main` ，用于处理用户大部分不需要特权的请求，以及主要的功能实现。
* *static* ：对应 Flask 框架中存储静态文件的目录，此目录存储设备管理平台使用的图片、js、css等文件。
* *static/thumbnail* ：此目录存储用户自定义的头像文件。
* *template* ：此目录存储设备管理平台渲染网页使用的模板。
* *models.py* ：对应 :ref:`dm-models` 中介绍的各类模型。
* *devices.py* ：对应 :ref:`dm-devices` 种介绍的各类设备模型。
* *config.py* ：对应 :ref:`dm-config` 中的配置文件。
* *manage.py* ：管理服务器的配置文件，包含了一系列自定义命令，你可以查看 :ref:`dm-structual-manage` 以了解更多。

各模块之间关系如下图所示：

|uml|


.. _dm-structual-manage:

管理器
-------------

`manage.py` 管理着顶点云设备管理平台。它提供了很多操作服务器的基础命令，如启动、初始化、测试等，你可以通过 `python manage.py <command>` 来运行不同命令。默认的顶点云设备管理平台管理器提供的命令有：

* `shell` ：启动交互式 Python 命令行并自动导入顶点云设备管理平台的各类模块
* `db` ：数据库迁移类命令，如 `db migrate` 、 `db init` 等
* `test` ：启动 `tests` 目录下的单元测试
* `init` ：初始化数据库，随机生成用户和数据
* `simple_init` ：简单初始化数据库，只加入五个特定的用户

.. _dm-app-factory:

工厂方法
----------------

`app/__init__.py` 中包含了设备管理平台的工厂方法，当你通过 `manage.py` 执行命令时， `manage.py` 会调用工厂方法生成一个应用实例。

工厂方法名为 `create_app` ，正如我们在 :ref:`dm-quickstart-expand` 中介绍的那样，修改 `manage.py` 的第 21 行实际是修改了工厂方法的参数。这个工厂方法根据传入的参数从 :ref:`dm-config` 中寻找对应表项（配置类），并使用该配置类生成服务器实例。

接下来请您阅读 :ref:`dm-blueprint` 。

.. |uml| image:: _static/dm-uml.png
