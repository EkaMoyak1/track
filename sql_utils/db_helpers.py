# sql_utils/db_helpers.py

import sqlite3
from flask import flash

def get_db_connection():
    conn = sqlite3.connect('date_source.db')
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Преобразует sqlite3.Row или tuple в словарь с пустыми строками вместо None"""
    # if isinstance(row, dict):
    #     return {key: (row[key] if row[key] is not None and row[key] != 'None' else '') for key in row.keys()}
    # elif hasattr(row, '_fields'):  # если это namedtuple
    #     return {key: (getattr(row, key) if getattr(row, key) is not None and row[key] != 'None' else '') for key in row._fields}
    # elif isinstance(row, (list, tuple)):  # если это список/кортеж
    #     return [value if value is not None and row[key] != 'None' else '' for value in row]
    # else:
    #     return row
    result = {}
    for key in row.keys():
        value = row[key]
        result[key] = value if value is not None and row[key] != 'None' else ''
    return result