from .db_helpers import get_db_connection
from flask import flash


def get_child_by_id(child_id, join_studio=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    if join_studio:
        query = """
            SELECT spisok.id, spisok.fio, spisok.date_bd, spisok.age, 
                   spisok_in_studio.id as id_table
            FROM spisok 
            JOIN spisok_in_studio ON spisok.id = spisok_in_studio.id_spisok  
            WHERE spisok.id = ?
        """
    else:
        query = "SELECT id, fio, date_bd, age FROM spisok WHERE id = ?"

    cursor.execute(query, (child_id,))
    child = cursor.fetchone()
    conn.close()
    return child


# Сохраняем все алиасы для совместимости
def get_child_in_spisok(child_id):
    return get_child_by_id(child_id, join_studio=False)


def get_child_in_studya_by_id(field_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT spisok.id, spisok.fio, spisok.date_bd, spisok.age,
               spisok_in_studio.napravlenie, spisok_in_studio.studio,
               spisok_in_studio.pedagog, spisok_in_studio.id as id_table
        FROM spisok_in_studio 
        JOIN spisok ON spisok_in_studio.id_spisok = spisok.id 
        WHERE spisok_in_studio.id = ?
    """, (field_id,))
    child = cursor.fetchone()
    conn.close()
    return child


# Дублирующая функция для совместимости
def get_child_in_studya_by_id_copy(field_id):
    return get_child_in_studya_by_id(field_id)