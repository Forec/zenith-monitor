.. _dm-quickstart:

快速上手
==========

此部分文档将带领您在一个假想的纯净环境中部署、配置、扩展自定义功能并启动顶点云设备管理平台。

假想环境
---------

有一天我意外获得了一台免费的 CVM，而我恰巧获得了一次得到顶点云设备管理平台源码的机会。这台云主机使用的操作系统为 CentOS 7.2，公网 IP 地址为 ``123.123.123.123`` ，已安装好 Python3、Pip以及 Pyvenv 并配置了环境变量。下面的指令均通过 SSH 远程操作。

.. code-block:: shell

    git clone https://github.com/Forec/zenith-monitor.git
    cd zenith-monitor/

我已经获得了顶点云应用程序服务器的源码，接下来使用一键配置脚本部署环境。

.. code-block:: shell

    cd settings
    ./setup.sh

很高兴看到配置脚本通知我部署完成。接下来测试一下代码是否能够在本地机器通过测试。

.. code-block:: shell

	cd ..
	source venv/bin/activate  # Windows 下请执行 venv/Scripts/activate.bat
	python manage.py test
	
非常顺利！测试脚本告诉我所有测试均已完成，顶点云设备管理平台各个基础模块能够在这台服务器上运转正常。

针对假想环境修改配置文件
--------------------------

鉴于顶点云提供的默认配置仅适用于 Forec 的史诗级笔记本，下面根据这台服务器的情况修改配置文件。编辑 `config.py` :

.. code-block:: shell

	nano config.py
	
我拷贝了一份 ``LinuxConfig`` 并重命名该子类为 ``MyConfig`` ，然后根据如下考虑对 ``MyConfig`` 做了一定修改：

* 我觉得顶点云默认使用的 SQLITE 数据库很方便，并且放置在源码根目录下也没什么问题，因此我决定保留默认配置中的 ``SQLALCHEMY_DATABASE_URI``
* 我想让世界上任何一个角落均能访问我的顶点云设备管理平台，因此我修改 ``ZENITH_SERVER_ADDRESS = '123.123.123.123'``
* 我要让顶点云设备管理平台用我的邮箱发送认证邮件。我的邮箱是 mymail@gmail.com，因此我修改如下部分：

 - ``MAIL_SERVER = 'smtp.gmail.com'``
 - ``MAIL_PORT = 25``
 - ``MAIL_USE_TLS = True``
 - ``MAIL_USERNAME = "mymail@gmail.com"``

* 我觉得邮箱的密码还是不要放在代码中比较好，因此我向环境变量添加了 ``MAIL_PASSWORD`` 值并保留了 ``MAIL_PASSWORD`` 的设置

看起来配置文件没什么值得修改的了，我决定按下 ``CTRL+X`` 保存配置文件，顺便检查一下新定义的配置类：

.. code-block:: python
	
   class MyConfig(Config):
    ZENITH_SERVER_ADDRESS = '123.123.123.123' # 服务器部署的域名/IP地址
    SERVER_NAME = ZENITH_SERVER_ADDRESS
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'work.db')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 25 # SSL is 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = "mymail@gmail.com"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
   
添加自定义类到表驱动
-----------------------------

我决定按照 :ref:`dm-config-add` 中的说法将我的自定义配置类添加到表驱动中。

向 `config.py` 的 `config` 字典中添加 ``'myconfig': MyConfig`` 后如下：

.. code-block:: python

   config = {
    'development' : DevelopmentConfig,      # 开发环境
    'linux': LinuxConfig,                   # 提供的 Linux 模板环境
    'windows': WindowsConfig,               # 提供的 Windows模板环境
    'testing' : TestingConfig,              # 测试环境
    'default' : DevelopmentConfig,          # 默认为开发环境
    'myconfig' : MyConfig					# 自定义添加的配置类
    }

之后修改 `manage.py` 的第 21 行为：

.. code-block:: python

    app = create_app('myconfig')

.. _dm-quickstart-runserver:

启动服务器
-----------------

顶点云设备管理平台可通过两种方式启动。我们推荐使用 `settings` 目录下的启动脚本，启动脚本使用 `gunicorn` 能够提高服务器的并发能力。

一键启动
>>>>>>>>>>

`settings` 目录提供了顶点云设备管理平台的启动脚本，您可以运行 `run.sh` （Linux 系统）或 `run.bat` （Windows 系统）来启动服务器。默认会开启在本机（127.0.0.1）的 5001 端口。您可以修改启动脚本中的 IP 地址和端口号。

手动启动
>>>>>>>>>>>

您也可以选择手动控制服务器的启动。通常在 Debug 情况下使用此方式，因为 Flask 对并发请求的原生支持并不很令人满意。

.. code-block:: shell
	
	source venv/bin/activate	# Windows 下请执行 venv/Scripts/activate.bat
	python manage.py runserver	# 您可以指定 -h 和 -p 参数，分别代表开放服务器的IP 地址和端口号

现在您可以从本机的浏览器访问您的服务器了。

.. _dm-quickstart-expand:

扩展自定义功能
-----------------

不得不说 Forec 的设计实在是太简陋了，为什么用户无法注册！幸好我学习过 `Flask`_ 框架，也许我应该自己添加这个功能？

在阅读了 :ref:`app-structual` 后，我了解了整个顶点云设备管理平台的结构，下面我准备添加这个简单的功能。

进入 `app/auth` 目录并编辑 `views.py` ：

.. code-block:: shell
	
	cd app/auth
	nano views.py
	
我在源码的 79 行发现了一句注释，原来默认的顶点云设备管理平台提供了注册接口，但将注册部分屏蔽掉了，反馈给用户的仅仅是展示界面。注册的视图函数如下所示。

.. code-block:: python

	@auth.route('/register', methods = ['GET', 'POST'])
	def register():
		# 展示状态，禁止注册
		return render_template('auth/test.html')
	#	if request.method == 'GET':
	#		if current_user.is_authenticated:
	#			flash('您已经登录，无需注册！')
	#			return redirect(url_for('main.home'))
	#		return render_template('auth/register.html')
	#	else:
	#		req = request.form.get('request')
			# ......
			# ......

我决定开放注册接口，因此我将被注释的部分取消注释，将视图函数中的第一句 `return` 删除。

.. code-block:: python

	@auth.route('/register', methods = ['GET', 'POST'])
	def register():
		# 展示状态，禁止注册
		# return render_template('auth/test.html')
		if request.method == 'GET':
			if current_user.is_authenticated:
				flash('您已经登录，无需注册！')
				return redirect(url_for('main.home'))
			return render_template('auth/register.html')
		else:
			req = request.form.get('request')
			if req is None:
				return jsonify({
					'code': 0   # 没有请求
				})
			req = json.loads(req)
			email = req.get('email')
			password = req.get('passwd')
			password2 = req.get('passwd2')
			nickname = req.get('nickname')
			if email is None or password is None or \
				password2 is None or nickname is None or \
				not verify_email(email) or not verify_nickname(nickname) or \
				password != password2:
				return jsonify({
					'code': 1   # 填写格式不对
				})
			user1 = User.query.filter_by(email = email).first()
			if user1 is not None:
				return jsonify({
					'code': 2      # 邮箱已被注册
				})

			user2 = User.query.filter_by(nickname = nickname).first()
			if user2 is not None:
				return jsonify({
					'code': 3      # 此昵称已被注册已被注册
				})
			user = User(email = email,
						nickname = nickname,
						password = password)
			db.session.add(user)
			db.session.commit()
			token = user.generate_confirmation_token()
			send_email(user.email,
					   '确认您的帐户',
					   'auth/email/confirm',
					   user=user,
					   token=token)
			flash('一封确认邮件已经发送到您填写的邮箱，'
				  '请查看以激活您的帐号')
			login_user(user)
			return jsonify({
				'code': 4
			})
	
我重新启动了服务器，现在注册接口已经打开。


接下来请您阅读 :ref:`dm-structual` 。

.. _Flask: http://flask.pocoo.org/
