# 作者：Forec
# 最后修改时间：2016-12-13
# 邮箱：forec@bupt.edu.cn
# 关于此文件：包含了 main 蓝本中使用到的全部 wtf 表单

from ..models import User
from ..devices import deviceNumbers
from flask import current_app
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, \
    TextAreaField, SelectField, PasswordField, \
    IntegerField
from wtforms.validators import Required, Length, \
    ValidationError

# ------------------------------------------------------------------
# 用户编辑自己个人资料的表单，昵称长度必须在 3 到 64 个字符之间，且必须唯一
class EditProfileForm(FlaskForm):
    thumbnail = FileField('上传头像')
    nickname = StringField('昵称',
        validators=[Length(3, 64, message='昵称长度必须在 3 ~ 64 个字符之间！')])
    about_me = TextAreaField('关于我',
        validators=[Length(0, 60, message='不能超过 40 个字符！')])
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

# -------------------------------------------------------------------------
# 用户修改设备的表单。
class DeviceEditForm(FlaskForm):
    name = StringField("设备名称",
        validators=[Required(),
                    Length(1, 64, message='设备名称不能超过 64 个字符')])
    about = TextAreaField("设备描述")
    type = SelectField('类型', coerce=int)

    def __init__(self, *args, **kwargs):
        super(DeviceEditForm, self).__init__(*args, **kwargs)
        self.type.choices = deviceNumbers.items()

    submit = SubmitField('确定')

    def validate_about(self, field):     # 限制设备描述在 200 字符内
        if len(field.data) > 200:
            raise ValidationError('设备描述过长，请限制在 200 个字符内')

# -------------------------------------------------------------------------
# 用户删除设备的表单。
class DeviceDeleteForm(FlaskForm):
    password = PasswordField('输入密码', validators=
        [Required(), Length(4,
                            64,
                            message='密码长度必须为 4 ~ 64 个字符')])
    submit = SubmitField('确定')

# --------------------------------------------------------------------------
# 用户搜索设备表单
class SearchForm(FlaskForm):
    key = StringField()
    go = SubmitField('搜索')

# ----------------------------------------------------------------------------
# 用户创建设备
class NewDeviceForm(FlaskForm):
    name = StringField("设备名",
        validators=[Required(),
                    Length(0, 64, message='设备名长度不能超过 64 个 ASCII 字符')])
    type = SelectField('设备类型', coerce=int)
    interval = IntegerField('检查周期', default=5)
    about = TextAreaField("设备描述")
    submit = SubmitField('创建')

    def __init__(self, *args, **kwargs):
        super(NewDeviceForm, self).__init__(*args, **kwargs)
        self.type.choices = deviceNumbers.items()

    def validate_about(self, field):     # 限制设备描述在 200 字符内
        if len(field.data) > 200:
            raise ValidationError('设备描述过长，请限制在100字内')
    def validate_interval(self, field):     # 限制设备描述在 200 字符内
        if field.data < 1:
            raise ValidationError('检查周期至少为 1 s！')