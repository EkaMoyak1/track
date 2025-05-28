from .db_helpers import get_db_connection

def get_events_by_id(event_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events_table WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    return event

def get_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events_table ORDER BY name")
    events = cursor.fetchall()
    conn.close()
    return [[field.replace('"', "") if isinstance(field, str) else field for field in event] for event in events]