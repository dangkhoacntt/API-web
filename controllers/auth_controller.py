from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from db import get_db_connection
import hashlib
import os
from models import create_user, get_user
from mail_config import mail  # Nhập khẩu mail từ mail_config.py

auth_bp = Blueprint('auth', __name__)

def generate_api_key():
    return hashlib.md5(os.urandom(16)).hexdigest() 

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember_me = request.form.get('remember_me')  # Lấy giá trị từ checkbox

        user = get_user(email, hash_password(password))
        if user:
            session['user_email'] = user['email']
            session['user_finances'] = user['finances']
            flash('Đăng nhập thành công!', 'success')

            response = redirect(url_for('main.home'))

            # Nếu người dùng chọn "Ghi nhớ mật khẩu", lưu email vào cookie
            if remember_me:
                response.set_cookie('user_email', user['email'], max_age=30*24*60*60)  # Cookie tồn tại 30 ngày
            else:
                response.set_cookie('user_email', '', expires=0)  # Xóa cookie nếu không chọn

            return response
        else:
            flash('Thông tin đăng nhập không chính xác. Vui lòng thử lại.', 'danger')

    # Kiểm tra xem có cookie 'user_email' không và tự động điền vào trường email
    user_email = request.cookies.get('user_email', '')
    return render_template('frontend/login.html', user_email=user_email)
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']

        if get_user(email):
            flash('Email đã được đăng ký.', 'danger')
        else:
            key_api = generate_api_key()  # Tạo khóa API
            create_user(email, hash_password(password), first_name, last_name, phone, key_api)
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('frontend/register.html')



@auth_bp.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_finances', None)
    flash('Bạn đã đăng xuất thành công.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        
        user = get_user(email)
        if user:
            token = hashlib.sha256(os.urandom(24)).hexdigest()
            reset_url = url_for('auth.reset_password_token', token=token, _external=True)
            msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[email])
            msg.body = f'Click the following link to reset your password: {reset_url}'
            mail.send(msg)

            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('Email not found.', 'danger')

    return render_template('frontend/reset_password.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if request.method == 'POST':
        new_password = request.form['new_password']
        hashed_password = hash_password(new_password)

        conn = get_db_connection()
        conn.execute('UPDATE user SET password = ? WHERE email = (SELECT email FROM user WHERE token = ?)', 
                     (hashed_password, token))
        conn.commit()
        conn.close()

        flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('frontend/reset_password.html')
