from db import get_db_connection

def create_user(email, password, first_name, last_name, phone, key_api, is_admin=0):
    conn = get_db_connection()
    conn.execute('INSERT INTO user (email, password, first_name, last_name, phone, key_api, is_admin) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (email, password, first_name, last_name, phone, key_api, is_admin))
    conn.commit()
    conn.close()


def get_user(email, password=None):
    conn = get_db_connection()
    if password:
        user = conn.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password)).fetchone()
    else:
        user = conn.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
    return user




def is_admin_user(email):
    conn = get_db_connection()
    user = conn.execute('SELECT is_admin FROM user WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user and user['is_admin'] == 1  # Trả về True nếu là admin
