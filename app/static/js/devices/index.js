function refresh(hashID) {
    $.post(window.url + '/show_status/', {
        'request':{
            'token': '9490544C18C15B21286685B41F825684',
            'email': 'test@test.com',
            'set':{
                'shutdown': 1
            }
        }
    }).done(function (data) {
        if ('list' in data){
            for (var key in data.list){     // key is device.code
                console.log(key);
                var status = data.list[key];
                var block = $('#'+key);
                if (status.warning == true){     // 是否告警
                    block.children('#Warning').text('设备告警');
                    block.children('#Warning').show();
                }
                else
                    block.children('#Warning').hide();
                block.children('#Temperature').text(status.temperature);
                block.children('#Name').text(status.name);
                block.children('#Interval').text(status.interval);

                var workblock = block.children('#Work')

                if (status.type === 'Bulb'){
                    // 电灯泡
                    block.children('#Type').text('照明');
                    if (status.work == true){        // 是否工作
                        workblock.children('#Working').text('设备正在工作');
                        workblock.children('#BulbVolume').text(status.volume);
                        workblock.children('#BulbCurrent').text(status.current);
                        workblock.children('#BulbPower').text(status.power);
                        workblock.children('#BulbFull').text(status.full);
                        workblock.children('#BulbLightDegree').text(status.lightDegree);
                        workblock.children('#BulbVolume').show();
                        workblock.children('#BulbCurrent').show();
                        workblock.children('#BulbPower').show();
                        workblock.children('#BulbFull').show();
                        workblock.children('#BulbLightDegree').show();
                    } else{
                        workblock.children('#Working').text('设备未工作');
                        workblock.children('#BulbVolume').hide();
                        workblock.children('#BulbCurrent').hide();
                        workblock.children('#BulbPower').hide();
                        workblock.children('#BulbFull').hide();
                        workblock.children('#BulbLightDegree').hide();
                    }
                } else if (status.type == 'TV'){
                    // 电视
                    block.children('#Type').text('电视');
                    if (status.work == true){        // 是否工作
                        workblock.children('#Working').text('设备正在工作');
                        workblock.children('#TVVolume').text(status.volume);
                        workblock.children('#TVVoiceVolume').text(status.voicevolume);
                        workblock.children('#TVCurrent').text(status.current);
                        workblock.children('#TVPower').text(status.power);
                        workblock.children('#TVImage').attr('src',window.url+'/static/tvs/' + status.image+'.png');
                        workblock.children('#TVCurrent').show();
                        workblock.children('#TVPower').show();
                        workblock.children('#TVImage').show()
                        workblock.children('#TVVolume').show();
                        workblock.children('#TVVoiceVolume').show();
                    } else{
                        workblock.children('#Working').text('设备未工作');
                        workblock.children('#TVVolume').hide();
                        workblock.children('#TVVoiceVolume').hide();
                        workblock.children('#TVCurrent').hide();
                        workblock.children('#TVPower').hide();
                        workblock.children('#TVImage').hide();
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

$(document).ready($(this).everyTime('2s', refresh));
console.log(window.url + '/show_status/');