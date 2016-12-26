window.url = 'http://10.201.14.176:5000';

function refresh() {
    $.post(window.url + '/show_status/', {
        'request':{
            'token': '9490544C18C15B21286685B41F825684',
            'email': 'test@test.com'
        }
    }).done(function (data) {
        if ('list' in data){
            for (var key in data.list){     // key is device.code
                var status = data.list[key];
                var block = $('#'+key);

                var deviceDate = 1000* status.last_seen;
                var currentDate = new Date().getTime();
                console.log(currentDate, deviceDate);
                if (currentDate - deviceDate > 2000 * status.interval){
                    block.children('#Warning').text('设备未在线！');
                    block.children('#Warning').addClass("btn btn-danger");
                    block.children('#Warning').show();
                    block.children('#Temperature').text('未知');
                    block.children('#Name').text(status.name);
                    block.children('#Interval').text('未知');
                    block.children('#Work').hide();
                } else {
                    if (status.warning == true){     // 是否告警
                        block.children('#Warning').text('设备告警');
                        block.children('#Warning').addClass("btn btn-danger");
                        block.children('#Warning').show();
                    }
                    else{
                        block.children('#Warning').hide();
                    }
                    block.children('#Temperature').text(status.temperature);
                    block.children('#Name').text(status.name);
                    block.children('#Interval').text(status.interval);

                    var workblock = block.children('#Work')
                    workblock.show();

                    workblock.children('#Volume').text(status.volume);
                    workblock.children('#Current').text(status.current);
                    workblock.children('#Power').text(status.power);
                    workblock.children('#Volume').show();
                    workblock.children('#Current').show();
                    workblock.children('#Power').show();

                    if (status.work == true){
                        workblock.children('#Working').text('设备正在工作');
                        workblock.children('#Open').text('关闭设备');
                    } else{
                        workblock.children('#Working').text('设备未工作');
                        workblock.children('#Open').text('开启设备');
                    }

                    if (status.type === 'Bulb'){
                        // 电灯泡
                        block.children('#Type').text('照明');
                        if (status.work == true){        // 是否工作
                            workblock.children('#BulbFull').text(status.full);
                            workblock.children('#BulbLightDegree').text(status.lightDegree);
                            workblock.children('#BulbFull').show();
                            workblock.children('#BulbLightDegree').show();
                        } else{
                            workblock.children('#BulbFull').hide();
                            workblock.children('#BulbLightDegree').hide();
                        }
                    } else if (status.type == 'TV'){
                        // 电视
                        block.children('#Type').text('电视');
                        if (status.work == true){        // 是否工作
                            workblock.children('#TVStation').text(status.station);
                            workblock.children('#TVStation').show();
                            workblock.children('#TVVoiceVolume').text(status.voice);
                            workblock.children('#TVVoiceVolume').show();
                            workblock.children('#TVImage').attr('src',window.url+'/static/tvs/' + status.image+'.png');
                            workblock.children('#TVImage').show()
                        } else{
                            workblock.children('#TVVoiceVolume').hide();
                            workblock.children('#TVImage').hide();
                        }
                    } else if (status.type == 'Air'){
                        // 空调
    //                    console.log(status.level);
                        block.children('#Type').text('空调');
                        if (status.work == true){        // 是否工作
                            workblock.children('#AirAir').text(status.air);
                            if (status.mode == true){
                                workblock.children('#AirMode').text('制热');
                            }else {
                                workblock.children('#AirMode').text('制冷');
                            }
                            workblock.children('#AirTarget').text(status.target);
                            workblock.children('#AirSpeed').text(status.speed);
                            workblock.children('#AirLevel').text(status.level);
                            workblock.children('#AirAir').show();
                            workblock.children('#AirLevel').show();
                            workblock.children('#AirTarget').show();
                            workblock.children('#AirMode').show();
                            workblock.children('#AirSpeed').show();
                        } else{
                            workblock.children('#AirAir').hide();
                            workblock.children('#AirLevel').hide();
                            workblock.children('#AirTarget').hide();
                            workblock.children('#AirMode').hide();
                            workblock.children('#AirSpeed').hide();
                        }
                    }
                }
            }
        } else if ('code' in data){
            var status = data.get('status');
        }
        //$('.device-block').text(JSON.stringify(data));
    }).fail(function (data) {
        console.log('失败');
    });
}

function setStatus() {
    $.ajax({
        url: window.url + '/set_device/',
        data: {
            'request':JSON.stringify({
                'token': '9490544C18C15B21286685B41F825684',
                'email': 'test@test.com',
                'code': 'CE683231033B',
                'set':{
                    'interval': 20,
                    'voice': 14
                }
            })
        },
        type: 'POST',
        success: function(response){
            console.log("成功，返回数据：" + response);
        },
        error: function(error){
            console.log("失败，错误："+error);
        }
    });
}

function getHistory() {
    $.ajax({
        url: window.url + '/get_history/',
        data: {
            'request':JSON.stringify({
                'token': '9490544C18C15B21286685B41F825684',
                'email': 'test@test.com',
                'code': 'CE683231033B',
                'time':{
                    'year': '2016',
                    'month': '12',
                    'day': '26',
                    'hour': '09',
                    'minute': '15',
                    'second': '00'
                },
                'period': 900,
                'inter': 300
            })
        },
        type: 'POST',
        success: function(response){
            for (var stamp in response){
                var status = response[stamp];
                console.log(stamp);
                console.log(status);
            }
        },
        error: function(error){
            console.log("失败，错误："+error);
        }
    });
}
$(document).ready(setTimeout("getHistory()", 1000));
//$(document).ready(setTimeout("setStatus()", 1000));
$(document).ready($(this).everyTime('2s', refresh));
console.log(window.url + '/show_status/');