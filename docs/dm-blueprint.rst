.. _dm-blueprint:

蓝本介绍
==========

此部分文档主要介绍顶点云设备管理平台中的两个蓝本： `main` 以及 `auth` ，以及如何创建新的自定义蓝本。

.. _dm-blueprint-auth:

Auth 蓝本
----------------

此蓝本主要用于授权用户，如注册、登录、重置密码等。蓝本位于 `app/auth` 目录下，结构为：

.. code-block:: shell

   - auth
     - __init__.py
     - forms.py
     - views.py
     
上面三个文件中， `__init__.py` 用于初始化蓝本 Auth，`forms.py` 定义了 Auth 蓝本视图函数需要使用的表单类，`views.py` 具体处理转发给 Auth 蓝本的请求。

关于 `views.py` 中的视图函数，请查阅 :ref:`dm-viewfunction-auth` 。


.. _dm-blueprint-main:

Main 蓝本
----------------

此蓝本主要用于处理用户服务请求。蓝本位于 `app/main` 目录下，结构为：

.. code-block:: shell

   - main
     - __init__.py
     - forms.py
     - views.py
     - errors.py
     
上面三个文件中， `__init__.py` 用于初始化蓝本 Main，`forms.py` 定义了 Main 蓝本视图函数需要使用的表单类，`views.py` 具体处理转发给 Main 蓝本的请求，`errors.py` 处理用户遇到的错误并使用服务器模板渲染错误界面。

对于 `views.py` 中的视图函数，请查阅 :ref:`dm-viewfunction-main` 。

自定义蓝本
-----------------------

关于蓝本的概念不属于本文档讨论范围，如果您尚不了解，可以参考 `Flask 文档中关于蓝本的部分 <http://flask.pocoo.org/docs/0.12/search/?q=blueprint>`_ 。

对于顶点云设备管理平台，如果您需要添加自定义蓝本，请在目录 `app` 下创建新的蓝本目录并添加您的自定义路由。

接下来请您阅读 :ref:`dm-models` 。
