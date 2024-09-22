from flask import Blueprint, render_template, session, redirect, url_for, flash
import sqlite3
from db import get_db_connection
user_list_bp = Blueprint('user_list', __name__)

def get_all_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email, key_api, created_at, status FROM user")
    users = [
        {'email': row[0], 'key_api': row[1], 'created_at': row[2], 'status': row[3]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return users
@user_list_bp.route('/admin/users')
def user_list():
    if 'admin_email' in session:
        users = get_all_users()
        return render_template('backend/user_list.html', users=users)
    flash('Truy cập bị từ chối. Chỉ dành cho quản trị viên.', 'danger')
    return redirect(url_for('admin.login'))


