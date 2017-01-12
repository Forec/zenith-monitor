.. _dm-installation:

部署
===========================

顶点云设备管理平台使用 Python3 编写，基于 Flask 框架，在部署前请确保您已经安装 Python3、Pip、Pyvenv 等，并已正确设置环境变量。我们推荐的 Python3 版本为 Python 3.5.0。有关 Python3 和 Flask 的介绍不在本文档范围内，如果您尚不了解，请参阅以下相关链接：

-	`Python3 快速上手指南 <https://docs.python.org/3/tutorial/index.html>`_
-	`Pip 安装指南 <https://pip.pypa.io/en/stable/installing/>`_
-	`Pyvenv 使用指南 <https://docs.python.org/3/library/venv.html>`_
-	`Flask 文档 <http://flask.pocoo.org/docs/0.12/>`_

获取源码
-------------

顶点云设备管理平台的源码托管在 `GitHub <https://github.com/Forec/zenith-monitor>`_ 上，您可以使用 Git 克隆仓库或直接通过 GitHub 下载源码的压缩包。假设您熟悉 Git，请通过以下命令获取源码。

.. code-block:: shell
    
    git clone https://github.com/Forec/zenith-monitor.git
    cd zenith-monitor
    
此时您应当已经进入顶点云设备管理平台的源码目录。

安装第三方支持
-------------------

顶点云设备管理平台使用到的所有第三方库均包含在需求文件 ``requirements.txt`` 中。您有两种方式部署。

注：为了减少部署困难，``requirements.txt`` 中不包含 OpenCV 相关库，如果您需要电视播放等功能，请自行安装 OpenCV 以及 `opencv-python` 以完成 OpenCV 对 Python 的支持。我在其它项目中给出过 OpenCV 的配置过程 ，您可在 `这里`_ 查看安装过程。

一键部署脚本
>>>>>>>>>>>>>>>>>>

顶点云设备管理平台为 Linux 提供了一键部署脚本，它位于 ``settings`` 下。您可以运行以下命令。

.. code-block:: shell
    
    cd settings
    ./setup.sh
	
如果您使用 Windows 系统，请参考下方的手动配置，或者如果您使用 Git Command，可以在 Git 的 Bash 命令行中运行 `setup.sh` 。
	
如果您的 Python 环境工作正常并且网络畅通，您应该可以看到终端中没有提示任何信息并且显示 *部署完成* 字样。

手动部署
>>>>>>>>>>>>>>>

您可以选择手动部署顶点云设备管理平台，流程如下：

.. code-block:: shell

	mkdir venv
	python3 -m venv venv/
	source venv/bin/activate		// Windows 系统此步骤为 venv/Scripts/activate.bat
	pip3 install -r requirements.txt --index-url https://pypi.douban.com/simple
	pip3 install gunicorn --index-url https://pypi.douban.com/simple
	python3 manager.py simple_init
	deactivate
	
如果您的 Python 环境工作正常并且网络畅通，此时顶点云设备管理平台应当已经部署完毕。

**请注意，默认情况下您安装的顶点云设备管理系统是不需要 OpenCV 的，因此无法提供虚拟电视的播放功能。** 如果您需要提供电视播放能力的设备，请将代码中两处注释掉的代码恢复（分别位于第 5 行和第 387 行）。

另：`clients` 目录下的模拟测试客户端中默认包含了 OpenCV 的头文件，您需要通过 `pip3 install opencv-python` 来获取第三方支持。或者将所有与 CV 相关的代码注释掉。

运行测试
----------------

顶点云设备管理平台提供了一部分单元测试，您可以运行单元测试以确保环境配置正常。

进入源码所在路径，运行 `python3 manage.py test` 。若测试结果显示通过则顶点云设备管理平台部署成功。

顶点云设备管理平台可运行在任何主流体系结构计算机以及任何操作系统上。接下来请您阅读 :ref:`dm-config` 以根据您的系统配置顶点云设备管理平台。

.. _这里: https://github.com/Forec/lan-ichat
