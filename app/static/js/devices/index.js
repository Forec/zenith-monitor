function refresh(hashID) {
    $.post(window.url + '/show_status/', {
        'request':{
            'token': '9490544C18C15B21286685B41F825684',
            'email': 'test@test.com'
        }
    }).done(function (data) {
        $('.device-block').text(JSON.stringify(data));
    }).fail(function (data) {
        console.log('失败');
    });
}

$(document).ready($(this).everyTime('2s', refresh));
console.log(window.url + '/show_status/');