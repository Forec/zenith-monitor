# 作者：Forec
# 最后修改时间：2016-12-13
# 邮箱：forec@bupt.edu.cn
# 关于此文件：包含了 main 蓝本中使用到的全部 wtf 表单

from ..models import User
from flask import current_app
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, \
    TextAreaField
from wtforms.validators import Required, Length, \
    ValidationError

# ------------------------------------------------------------------
# 用户编辑自己个人资料的表单，昵称长度必须在 3 到 64 个字符之间，且必须唯一
class EditProfileForm(FlaskForm):
    thumbnail = FileField('上传头像')
    nickname = StringField('昵称',
        validators=[Required(message='昵称必须填写！'),
                    Length(3, 64, message='昵称长度必须在 4 ~ 64 个字符之间！')])
    url = StringField('监控视频源')
    about_me = TextAreaField('关于我',
        validators=[Length(0, 60, message='不能超过 200 个字符！')])
    submit = SubmitField('提交')

    def validate_nickname(self, field):     # 验证昵称未被其他用户使用
        if field.data != current_user.nickname and \
            User.query.filter_by(nickname=field.data).first():
            raise ValidationError('该昵称已被使用.')
    def validate_thumbnail(self, field):     # 验证昵称未被其他用户使用
        if not field.has_file():
            return
        valid = False
        for _suffix in current_app.config['ZENITH_VALID_THUMBNAIL']:
            if _suffix in field.data.filename:
                valid = True
        if not valid:
            raise ValidationError('上传的头像必须为 .jpg/'
                                  '.jpeg/.png/.ico 格式之一！')