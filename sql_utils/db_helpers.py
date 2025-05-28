# sql_utils/db_helpers.py

import sqlite3
from flask import flash

def get_db_connection():
    conn = sqlite3.connect('date_source.db')
    conn.row_factory = sqlite3.Row
    return conn