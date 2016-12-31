# 作者：Forec
# 最后修改日期：2016-12-20
# 邮箱：forec@bupt.edu.cn
# 关于此文件：此文件包含了服务器认证部分的视图函数，包括登录、注册、密码重置等。
# 蓝本：auth

from flask       import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .           import auth
from .forms      import LoginForm, RegistrationForm, ChangePasswordForm,\
                        ChangeEmailForm, PasswordResetForm, \
                        PasswordResetRequestForm
from .. import db
from ..models import User
from ..email import send_email
import json, re


# ----------------------------------------------------------------
# rules 函数提供了 “注册须知” 界面的入口
@auth.route('/rules')
def rules():
    return render_template('auth/rules.html')

def verify_email(email):
    if len(email) > 7 and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
        return True
    return False

def verify_nickname(nickname):
    invalid = ['?', '/', '=', '>', '<', '!', ',', ';', '.', '\\']
    for inv in invalid:
        if inv in nickname:
            return False
    return True

# ----------------------------------------------------------------
# login 函数提供了登录界面入口
@auth.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        return render_template('login.html')
    else:
        req = request.form.get('request')
        if req is None:
            return 'fail'
        req = json.loads(req)
        email = req.get('email')
        password = req.get('passwd')
        if email is None or password is None or \
            not verify_email(email):
            return jsonify({
                'code': False
            })
        user = User.query.filter_by(email = email).first()
        if user is None or not user.verify_password(password):
            return jsonify({
                'code': False
            })
        else:
            login_user(user)
            return jsonify({
                'code': True
            })
            return redirect(url_for('main.home'))


# -----------------------------------------------------------------
# logout 函数提供了登出操作，登出后默认重定向到登陆入口
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经登出')
    return redirect(url_for('auth.login', _external=True))

# ------------------------------------------------------------------
# register 函数提供了注册入口
@auth.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        if current_user.is_authenticated:
            flash('您已经登录，无需注册！')
            return redirect(url_for('main.home'))
        return render_template('register.html')
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

# -------------------------------------------------------------------
# confirm 函数提供了用户注册邮箱激活入口，根据向用户发送的激活链接尾部的
# token 校验用户是否合法。
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index', _external=True))
    if current_user.confirm(token):
        flash('您已经验证了您的邮箱！感谢您的支持！')
    else:
        flash('此验证链接无效或已过期！')
    return redirect(url_for('main.home', _external=True))

# --------------------------------------------------------------------
# resend_confirmation 用于在用户未收到激活邮件时重发。
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
        # 生成新的激活 token
    send_email(current_user.email,
               '确认您的帐户',
               'auth/email/confirm',
               user = current_user,
               token = token)
    flash('一封确认邮件已经发送到您注册时填写的邮箱，'
          '请查看以激活您的帐号')
    return redirect(url_for('main.index', _external=True))

# --------------------------------------------------------------------
# change_password 为用户修改密码的视图函数。
@auth.route('/change-password', methods=['POST'])
def change_password():
    req = request.form.get('request')
    if req is None:
        return jsonify({
            'code': 0   # 没有请求
        })
    req = json.loads(req)
    email = req.get('email')
    password = req.get('passwd')
    token = req.get('token')
    newpassword = req.get('newpasswd')
    if email is None or password is None or \
        token is None or newpassword is None:
            return jsonify({
                'code': 1   # 填写格式不对
            })
    user = User.query.filter_by(email = email).first()
    if user is None or user!=current_user or \
            not user.verify_token(token) or \
            not user.verify_password(password):
        return jsonify({
            'code': 2      # 认证失败
        })
    user.password = newpassword
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'code': 3
    })

# ----------------------------------------------------------------------
# change_email_request 为用户重置邮箱请求入口。
@auth.route('/change-email-request', methods = ['POST'])
def change_email_request():
    req = request.form.get('request')
    if req is None:
        return jsonify({
            'code': 0   # 没有请求
        })
    req = json.loads(req)
    email = req.get('email')
    password = req.get('passwd')
    token = req.get('token')
    newemail = req.get('newemail')
    if email is None or password is None or \
        token is None or newemail is None or \
        not verify_email(email) or \
        not verify_email(newemail):
            return jsonify({
                'code': 1   # 填写格式不对
            })
    user = User.query.filter_by(email = email).first()
    user2 = User.query.filter_by(email=newemail).first()
    if user2 is not None or user is None or \
            user!=current_user or \
            not user.verify_token(token) or \
            not user.verify_password(password):
        return jsonify({
            'code': 2      # 认证失败
        })
    email_token = current_user.generate_email_change_token(newemail)
    send_email(newemail,
            '确认您的邮箱',
            'auth/email/change_email',
            user = current_user,
            token = email_token)
    return jsonify({
        'code': 3
    })

# --------------------------------------------------------------------
# change_email 用于验证用户重置邮箱后的激活链接。
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('您的电子邮箱已经更新')
    else:
        flash('非法请求')
    return redirect(url_for('main.index',
                            _external=True))

# --------------------------------------------------------------------
# password_reset_request 为用户重置密码入口。
@auth.route('/password_reset_request/', methods=['GET', 'POST'])
def password_reset_request():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        return render_template('reset.html')
    else:
        req = request.form.get('request')
        if req is None:
            return jsonify({
                'code': 0   # 没有请求
            })
        req = json.loads(req)
        email = req.get('email')
        if email is None or not verify_email(email):
            return jsonify({
                'code': 1   # 填写格式不对
            })
        user = User.query.filter_by(email = email).first()
        if user is None:
            return jsonify({
                'code': 2      # 假装成功
            })
        token = user.generate_reset_token()
        send_email(user.email,
                    '重置您的密码',
                    'auth/email/reset_password',
                    user = user,
                    token = token,
                    next = request.args.get('next'))
        flash('一封指导您重置密码的邮件已经发送到您注册时'
                  '填写的邮箱，请查看邮件并重置您的密码')
        return jsonify({
            'code': 2       # 成功
        })

# -------------------------------------------------------------------
# password_reset 函数用于验证用户重置密码请求 token 的合法性。
@auth.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        return render_template('password_reset.html', token=token)
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
        if email is None or password is None or \
            password2 is None or \
            not verify_email(email) or \
            password != password2:
            return jsonify({
                'code': 0   # 填写格式不对
            })
        user = User.query.filter_by(email = email).first()
        if user is None:
            return jsonify({
                'code': 2      # 不存在相关账户
            })
        if user.reset_password(token, password):
            return jsonify({
                'code': 3
            })
        else:
            return jsonify({
                'code': 2
            })

# ------------------------------------------------------------------
# secure_center 返回安全中心界面。
@auth.route('/secure_center')
@login_required
def secure_center():
    return render_template('secure_center.html')

# -------------------------------------------------------------------
# before_request 注册了用户未激活邮箱时的跳转接口。
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
           and request.endpoint[:5] != 'auth.' \
           and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed',
                                    _external=True))

# -------------------------------------------------------------------
# unconfirmed 函数提供了未验证的界面。
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index', _external=True))
    return render_template('unconfirmed.html')
