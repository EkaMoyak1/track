from .db_helpers import get_db_connection, dict_from_row
import sqlite3


def get_events_by_id(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events_table WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    if event:
        return dict_from_row(event)
    return None

def get_events():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, t.name AS type_event_name
        FROM events_table e
        LEFT JOIN event_type t ON e.type_event_id = t.id
    """)
    events = cursor.fetchall()
    conn.close()
    return [dict_from_row(event) for event in events]


# типы конкурсов
def get_event_types():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event_type")
    types = cursor.fetchall()
    conn.close()
    return [dict_from_row(row) for row in types]

def get_event_type_by_id(event_type_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event_type WHERE id = ?", (event_type_id,))
    event_type = cursor.fetchone()
    conn.close()

    if event_type:
        return dict_from_row(event_type)
    return None