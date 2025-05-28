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