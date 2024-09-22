from flask import Blueprint, render_template, session, redirect, url_for, request
import sqlite3
import os
import secrets

user_bp = Blueprint('user', __name__)

def get_user_data(user_email):
    conn = sqlite3.connect('database.db')  # Thay đổi với đường dẫn tới database của bạn
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE email = ?", (user_email,))
    columns = [column[0] for column in cursor.description]  # Lấy tên cột
    user_data = cursor.fetchone()

    # Chuyển đổi thành từ điển
    if user_data:
        user_dict = dict(zip(columns, user_data))
    else:
        user_dict = None

    conn.close()
    return user_dict

def update_api_key(user_email):
    new_api_key = secrets.token_hex(32)  # Tạo API key mới
    conn = sqlite3.connect('database.db')  # Thay đổi với đường dẫn tới database của bạn
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET key_api = ? WHERE email = ?", (new_api_key, user_email))
    conn.commit()
    conn.close()
    return new_api_key

@user_bp.route('/profile')
def profile():
    if 'user_email' in session:
        user_data = get_user_data(session['user_email'])
        api_key = user_data.get('key_api') if user_data else None  # Lấy api_key nếu có
        return render_template('frontend/profile.html', user=user_data, api_key=api_key)
    return redirect(url_for('auth.login'))

@user_bp.route('/profile/update_api_key', methods=['POST'])
def update_api_key_route():
    if 'user_email' in session:
        new_api_key = update_api_key(session['user_email'])  # Cập nhật API key
        return redirect(url_for('user.profile'))  # Chuyển hướng về trang profile
    return redirect(url_for('auth.login'))
