.. _dm-ajax:

Ajax 异步加载
==================

此部分文档主要介绍顶点云设备管理平台的 Ajax 异步加载。此部分文档由 `non1996`_ 编辑。

顶点云设备管理平台通过 DevExtreme 框架实现网页操控设备，定时获取设备状态，及设备状态可视化等功能。

.. _dm-js-graph-models-definition-and-function:

JavaScript 图表模型定义及功能
-------------------------------------

.. _dm-polyline-model:

折线图模型
>>>>>>>>>>>>>>>>>>


折线图用于显示设备电流值或 CPU 利用率的变化情况。以电流变化情况为例：

.. code-block:: javascript

	dxChart({
		dataSource: line_chart_data_source,
		commonSeriesSettings: {
		argumentField: "id",
		point: { visible: true, size: 5, hoverStyle: {size: 7, border: 0, color: 'inherit'} },
		line: {width: 1, hoverStyle: {width: 1}}
	},
	series: [
		{ valueField: "part1", name: "电流", color: "#68b828" }
	],
	legend: {
		position: 'inside',
		paddingLeftRight: 5
	},
	commonAxisSettings: {
		label: {
			visible: false
		},
		grid: {
			visible: true,
	    	color: '#f9f9f9'
		}
	},
	valueAxis: {
		max: 25
	},
	argumentAxis: {
		valueMarginsEnabled: false
	},
	}).data('iCount', i);

.. _dm-barchart-model:

柱状图模型
>>>>>>>>>>>>>>

柱状图用于显示电压或内存使用的变化情况：

.. code-block:: javascript

	dxChart({
		dataSource: [
			{id: ++i, 	sales: 1},
			{id: ++i, 	sales: 2},
			{id: ++i, 	sales: 3},
			{id: ++i, 	sales: 4},
			{id: ++i, 	sales: 5},
			{id: ++i, 	sales: 4},
			{id: ++i, 	sales: 5},
			{id: ++i, 	sales: 6},
			{id: ++i, 	sales: 7},
			{id: ++i, 	sales: 6},
			{id: ++i, 	sales: 5},
			{id: ++i, 	sales: 4},
			{id: ++i, 	sales: 5},
			{id: ++i, 	sales: 4},
			{id: ++i, 	sales: 4},
			{id: ++i, 	sales: 3},
			{id: ++i, 	sales: 4},
		],
		series: {
			argumentField: "id",
			valueField: "sales",
			name: "Sales",
			type: "bar",
			color: '#7c38bc'
		},
		commonAxisSettings: {
			label: {
				visible: false
			},
			grid: {
				visible: false
			}
		},
		legend: {
			visible: false
		},
		argumentAxis: {
			valueMarginsEnabled: true
		},
		valueAxis: {
			max: 12
		},
		equalBarWidth: {
			width: 11
		}
	}).data('iCount', i);

.. _dm-piechart-model:
	
饼图模型
>>>>>>>>>>>>>

饼图根据不同设备显示如室内温度，电灯饱和度等信息。

.. code-block:: javascript

	dxPieChart({
			dataSource: doughnut1_data_source,
			tooltip: {
				enabled: false,
				format:"millions",
				customizeText: function() {
					return this.argumentText + "<br/>" + this.valueText;
				}
			},
			size: {
				height: 90
			},
			legend: {
				visible: false
			},
			series: [{
				type: "doughnut",
				argumentField: "region"
			}],
			palette: ['#5e9b4c', '#6ca959', '#b9f5a6'],
		});

.. _dm-stock-model:		
		
股价图模型
>>>>>>>>>>>>>>>>

股价图用于显示设备温度变化。

.. code-block:: javascript

	dxChart({
			dataSource: realtime_network_stats,
			commonSeriesSettings: {
				type: "area",
				argumentField: "id"
			},
			series: [
				{ valueField: "x1", name: "Packets Sent", color: '#7c38bc', opacity: .4 },
				{ valueField: "x2", name: "Packets Received", color: '#000', opacity: .5},
			],
			legend: {
				verticalAlignment: "bottom",
				horizontalAlignment: "center"
			},
			commonAxisSettings: {
				label: {
					visible: false
				},
				grid: {
					visible: true,
					color: '#f5f5f5'
				}
			},
			legend: {
				visible: false
			},
			argumentAxis: {
				valueMarginsEnabled: false
			},
			valueAxis: {
				max: 500
			},
			animation: {
				enabled: false
			}
		}).data('iCount', i);

.. _dm-dashboard-model:
	
仪表盘模型
>>>>>>>>>>>>>>>

.. code-block:: javascript

	dxCircularGauge({	
			scale: {
				startValue: 0,
				endValue: 100,
				majorTick: {
					tickInterval: 25
				}
			},
			rangeContainer: {
				palette: 'pastel',
				width: 3,
				ranges: [
					{ startValue: 0, endValue: 25, color: "#68b828" },
					{ startValue: 25, endValue: 50, color: "#faff01" },
					{ startValue: 50, endValue: 75, color: "#ffb801" },
					{ startValue: 75, endValue: 100, color: "#ff3201" },
				],
			},
			value: 100,
			valueIndicator: {
				offset: 10,
				color: '#7c38bc',
				type: 'triangleNeedle',
				spindleSize: 12
			}
		});

.. _dm-spinner-model:
		
旋钮模型
>>>>>>>>>>>>>

旋钮主要用于控制设备属性，如电视音量，空调温度等。

.. code-block:: javascript

	$(".knob").knob({
			max: 300,
			min: 0,
			thickness: .3,
			fgColor: '#40bbea',
			bgColor: '#f0f0f0',
			'release':function(e){
				//action
			}
		});

.. _dm-main-device-js:
		
各设备页面主要 JavaScript 脚本	
-----------------------------------

.. _dm-global-functions:

页面共有函数
>>>>>>>>>>>>>>>>>

* `getAjaxFromServer()` ：以用户秘钥，用户邮箱，设备号为参数，向服务器发送 Ajax 请求，获取对应设备的实时信息并调用设置函数改变数据和图表的显示。

* `myElectricityChange(range)` ：参数为当前电流值，向设备电流图添加新的样值。

* `myVoltageGraphChange(range)` ：参数为当前电压值，向设备电压图添加新的样值。

* `myEleAndVolChange(vol, ele, pow)` ：参数为当前电压、电流、功率值，调用函数 `myElectricityChange` 和 `myVoltageGraphChange` 对电流和电压以及功率值进行设置。

* `myDegreeStateChange(range)` ：参数为当前设备温度，向设备温度图添加新的样值。

* `closeEquipment(type)` ：参数为按钮状态。响应函数，用户点击开启/关闭按钮时调用，向服务器发送ajax请求，执行对设备的开/关操作。

* `upperEquipmentInterval()` ：增加设备汇报状态周期。
	
* `lowerEquipmentInterval()` ：降低设备汇报状态周期。

.. _dm-bulb-functions:

照明设备
>>>>>>>>>>>>>

* `mySaturabilityChange(range)` ：参数为当前光线饱和度值，设置饱和度及其饼图。
	
* `setBrightness(up)` ：参数为用户点击按钮的类型，响应函数，用户点击设置电灯亮度的按钮时调用，向服务器发出ajax请求以改变电灯亮度。

.. _dm-air-functions:

空调
>>>>>>>>

* `switchSpeed(up)` ：参数为按键类型。响应函数，向服务器发出ajax请求改变空调风速，风速范围 1-5。

* `lowerPowerConsumption()` 和 `upperPowerConsumption()` ：响应函数，控制空调功耗等级，功耗范围为1-3。

* `setColdHotMode()` ：响应函数，控制空调制冷或制热模式间切换。

* `setDegree()` ：响应函数，用户释放旋钮时触发，控制空调温度。

.. _dm-tv-functions:

电视
>>>>>>>>>>>>

* `myTelevisionChange(src)` ：参数为电视画面的 url，函数接收服务器发来的电视截图 url，并将 img 标签属性更新。

* `switchChannel(up)` ：参数为按键类型，响应函数，控制电视频道切换。

* `setVoice()` ：响应函数，用户释放旋钮时触发，控制电视音量大小。

接下来请您阅读 :ref:`dm-test` 。

.. _non1996: https://github.com/non1996
