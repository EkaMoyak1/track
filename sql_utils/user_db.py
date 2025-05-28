# sql_utils/user_db.py

from .db_helpers import get_db_connection
from flask import flash

def check_user_credentials(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teacher WHERE fio=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_teacher(user_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_name == 'admin' or user_name is None:
        cursor.execute("SELECT * FROM teacher WHERE fio <> 'admin'")
    else:
        cursor.execute("SELECT * FROM teacher WHERE fio = ?", (user_name,))
    teachers = cursor.fetchall()
    conn.close()
    return teachers

def add_super_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO teacher (FIO, password) VALUES (?, ?)", ('admin', 'cdomir2024'))
    conn.commit()
    conn.close()