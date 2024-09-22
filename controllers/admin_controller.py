import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from db import get_db_connection
import hashlib
import os
from models import create_user, get_user
from flask import jsonify

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)  # Cấu hình để ghi log ở mức độ DEBUG
logger = logging.getLogger(__name__)  # Tạo logger

def generate_api_key():
    return hashlib.md5(os.urandom(16)).hexdigest()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

admin_bp = Blueprint('admin', __name__)

def is_admin_user(email):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM user WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    
    # Kiểm tra xem email có tồn tại và is_admin có phải là 1 không
    logger.debug(f"Checking if user {email} is admin.")
    return result is not None and result[0] == 1

@admin_bp.route('/admin')
def admin_dashboard():
    if 'admin_email' in session and is_admin_user(session['admin_email']):
        logger.info(f"Admin {session['admin_email']} accessed the dashboard.")
        return render_template('backend/home.html')
    
    logger.warning(f"Access denied for {session.get('admin_email', 'unknown')} to admin dashboard.")
    flash('Truy cập bị từ chối. Chỉ dành cho quản trị viên.', 'danger')
    return redirect(url_for('admin.login'))

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user(email, hash_password(password))
        if user and is_admin_user(email):
            session['admin_email'] = user['email']
            flash('Đăng nhập admin thành công!', 'success')
            logger.info(f"Admin {email} logged in successfully.")
            return redirect(url_for('admin.admin_dashboard'))
        else:
            logger.warning(f"Failed login attempt for {email}.")
            flash('Tài khoản không phải là admin hoặc thông tin đăng nhập không chính xác.', 'danger')

    return render_template('backend/login.html')

# Hàm ghi lại log khi API được sử dụng
def log_api_usage(user_id, key_api, link_api, action, success):
    conn = get_db_connection()
    conn.execute('INSERT INTO api_usage (user_id, key_api, link_api, action, success) VALUES (?, ?, ?, ?, ?)',
                 (user_id, key_api, link_api, action, success))
    conn.commit()
    conn.close()

# Route cho API request
@admin_bp.route('/api/v1/resource', methods=['POST'])
def resource():
    api_key = request.headers.get('API-Key')
    user = get_user_from_key_api(api_key)

    if user:
        # Logic xử lý hành động của API...
        success = True  # Hoặc False nếu gặp lỗi
        log_api_usage(user['id'], api_key, request.path, request.method, success)  # Sử dụng api_key
        return jsonify({"message": "Success"}), 200
    else:
        log_api_usage(None, api_key, request.path, request.method, False)
        return jsonify({"message": "Invalid API Key"}), 401


# Hàm để lấy chi tiết sử dụng API dựa trên key_api
def get_api_usage_details(key_api):
    conn = get_db_connection()
    usage_details = conn.execute(
        'SELECT link_api, action, success, usage_timestamp FROM api_usage WHERE key_api = ? ORDER BY usage_timestamp DESC',
        (key_api,)
    ).fetchall()
    conn.close()
    return usage_details
def get_user_from_key_api(key_api):
    if not key_api:
        return None  # Trả về None nếu không có key_api

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE key_api = ?", (key_api,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            'id': user[0],  # Giả sử cột 'id' là cột đầu tiên trong bảng `user`
            'email': user[1],  # Giả sử cột 'email' là cột thứ hai
            'key_api': user[6],  # Giả sử cột 'key_api' là cột thứ bảy (thay đổi nếu vị trí khác)
            # Thêm các cột khác nếu cần
        }
    return None  # Trả về None nếu không tìm thấy người dùng

def log_api_usage(user_id, key_api, link_api, action, success):
    conn = get_db_connection()  # Mở kết nối
    try:
        print(f"Logging API usage: {user_id}, {key_api}, {link_api}, {action}, {success}")
        conn.execute('INSERT INTO api_usage (user_id, key_api, link_api, action, success) VALUES (?, ?, ?, ?, ?)',
                     (user_id, key_api, link_api, action, success))
        conn.commit()
        print("API usage logged successfully.")
    except sqlite3.Error as e:
        print(f"Error logging API usage: {e}")
    finally:
        conn.close()  # Đảm bảo đóng kết nối ở đây

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Để truy cập dữ liệu như từ điển
    return conn

@admin_bp.route('/api/user/<key_api>/usage', methods=['GET'])
def get_api_usage(key_api):
    conn = get_db_connection()
    usage_details = conn.execute(
        'SELECT success, usage_timestamp FROM api_usage WHERE key_api = ? ORDER BY usage_timestamp ASC',
        (key_api,)
    ).fetchall()
    conn.close()

    # Chuyển đổi dữ liệu thành dạng list để dễ trả về JSON
    usage_data = [{'success': row[0], 'usage_timestamp': row[1]} for row in usage_details]

    return jsonify(usage_data)