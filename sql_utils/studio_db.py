from .db_helpers import get_db_connection

def get_napr():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spr_napravlenie")
    directions = cursor.fetchall()
    conn.close()
    return directions

def get_siudio():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spr_studya")
    studios = cursor.fetchall()
    conn.close()
    return studios

def get_all_studios():
    conn = get_db_connection()
    studios = conn.execute("SELECT id, name FROM spr_studya").fetchall()
    conn.close()
    return [dict(studio) for studio in studios]

def get_all_directions():
    conn = get_db_connection()
    directions = conn.execute("SELECT id, name FROM spr_napravlenie").fetchall()
    conn.close()
    return [dict(direction) for direction in directions]

def get_all_teachers():
    conn = get_db_connection()
    teachers = conn.execute("SELECT id, FIO FROM teacher").fetchall()
    conn.close()
    return [dict(teacher) for teacher in teachers]

def get_all_event_types():
    conn = get_db_connection()
    event_types = conn.execute("SELECT id, name FROM event_type").fetchall()
    conn.close()
    return [dict(et) for et in event_types]