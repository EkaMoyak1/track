# sql_utils/db_helpers.py

import sqlite3
from flask import flash

def get_db_connection():
    conn = sqlite3.connect('date_source.db')
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Преобразует sqlite3.Row или tuple в словарь с пустыми строками вместо None"""

    result = {}
    for key in row.keys():
        value = row[key]
        result[key] = value if value is not None and row[key] != 'None' else ''
    return result