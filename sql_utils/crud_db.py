from .db_helpers import get_db_connection
from flask import flash, request
from sql_utils.child_db import get_child_in_studya_by_id
import sqlite3

def setup_db():
    try:
        conn = get_db_connection()
        cursor_db = conn.cursor()
        sql_create = '''CREATE TABLE IF NOT EXISTS user_settings (
                        id TEXT PRIMARY KEY,
                        year_1 INTEGER DEFAULT 2024,
                        year_2 INTEGER DEFAULT 2025
                         );'''
        cursor_db.execute(sql_create)
        conn.commit()
        conn.close()
    except Exception as e:
        flash(f'Ошибка обновления при запуске: {e}', 'error')


def save_in_date_table(request):
    try:
        id_spisok = request.form['id_spisok']
        id_events_table = request.form['id_events_table']
        doc_type = request.form['doc_type']
        saved_file_name = request.form['saved_file_name']
        field_id = request.form['field_id']
        file = request.files['fileInput']
        original_name = file.filename
        ext = original_name.split('.')[-1]
        saved_file_name += '.' + ext

        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO data_table (id_spisok, id_spisok_in_studio, id_events_table, result, original_name, file)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_spisok, field_id, id_events_table, doc_type, original_name, saved_file_name))

        conn.commit()
        flash('Запись успешно добавлена', 'success')

    except KeyError as e:
        flash(f'Ошибка: отсутствует поле {e}', 'error')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
    finally:
        conn.close()


def update_in_data_table(request):
    """Update competition data"""
    record_id = request.form.get('record-id')
    id_spisok = request.form.get('id_spisok')
    id_events_table = request.form.get('id_events_table')
    result = request.form.get('id_doc_type')
    file = request.form.get('saved_file_name')
    original_name = request.form.get('original_file_name')
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        if not original_name:
            cursor.execute("""
                UPDATE data_table
                SET id_spisok = ?, id_events_table = ?, result = ?
                WHERE id = ?
            """, (id_spisok, id_events_table, result, record_id))
        else:
            cursor.execute("""
                UPDATE data_table
                SET id_spisok = ?, id_events_table = ?, result = ?, file = ?, original_name = ?
                WHERE id = ?
            """, (id_spisok, id_events_table, result, file, original_name, record_id))
        conn.commit()
        flash('Запись успешно изменена', 'success')
    except KeyError as e:
        flash(f'Ошибка: отсутствует поле {e}', 'error')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
    finally:
        conn.close()


def delete_in_data_table(record_id):
    """Delete competition data"""
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute('DELETE FROM data_table WHERE id = ?', (record_id,))
        conn.commit()
        flash('Запись успешно удалена', 'success')
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
    finally:
        conn.close()


def add_in_spisok_in_studio(request):
    """Add child to studio"""
    id_ch = request.form['fio']
    napravlenie = request.form['id_napr_table']
    studio = request.form['id_studio']
    pedagog = request.form['id_teacher']
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO spisok_in_studio (id_spisok, napravlenie, studio, pedagog)
            VALUES (?, ?, ?, ?)
        """, (id_ch, napravlenie, studio, pedagog))
        conn.commit()
        flash('Ребенок успешно добавлен в студию', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
    finally:
        conn.close()


def add_in_spisok(request):
    """Add new child"""
    fio = request.form['fio1']
    date_bd = request.form['date_bd']
    age = request.form['age']
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO spisok (fio, date_bd, age)
            VALUES (?, ?, ?)
        """, (fio, date_bd, age))
        conn.commit()
        flash('Ребенок успешно добавлен', 'success')
        return {'fio': fio, 'dr': date_bd, 'age': age}
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
        return {'result': False}
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return {'result': False}
    finally:
        conn.close()


def add_in_event(request):
    """Add new event"""
    name = request.form['name']
    opisanie = request.form['opisanie']
    srock = request.form['srock']
    resultat_date = request.form['resultat_date']
    level = request.form['level']
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events_table (name, opisanie, srok_podachi_date, result_date, level)
            VALUES (?, ?, ?, ?, ?)
        """, (name, opisanie, srock, resultat_date, level))
        conn.commit()
        flash('Конкурс успешно добавлен', 'success')
        return {"result": True}
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
        return {"result": False}
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return {"result": False}
    finally:
        conn.close()


def edit_in_spisok(request, child_id):
    """Edit child information"""
    try:
        date_bd = request.form['date_bd']
        age = request.form['age']
        fio = request.form['fio']
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE spisok
            SET date_bd=?, age=?, fio=?
            WHERE id = ?
        """, (date_bd, age, fio, child_id))
        conn.commit()
        flash('Ребенок успешно изменен', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception:
        flash('Ошибка при записи', 'error')
    finally:
        conn.close()


def edit_in_spisok_studya(request, field_id):
    """Edit child information in studio"""
    try:
        date_bd = request.form['date_bd']
        age = request.form['age']
        napravlenie = request.form['id_napr_table']
        studio = request.form['id_studio']
        pedagog = request.form['id_teacher']
        child = get_child_in_studya_by_id(field_id)
        child_id = child[0]
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        # Update child info
        cursor.execute("""
            UPDATE spisok
            SET date_bd=?, age=?
            WHERE id = ?
        """, (date_bd, age, child_id))
        # Update studio info
        cursor.execute("""
            UPDATE spisok_in_studio
            SET napravlenie=?, studio=?, pedagog=?
            WHERE id = ?
        """, (napravlenie, studio, pedagog, field_id))
        conn.commit()
        flash('Ребенок успешно изменен', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception:
        flash('Ошибка при записи', 'error')
    finally:
        conn.close()


def edit_in_events(request, event_id):
    """Edit event information"""
    try:
        name = request.form['name']
        opisanie = request.form['opisanie']
        srok_podachi_date = request.form['srok_podachi_date']
        result_date = request.form['result_date']
        level = request.form['level']
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE events_table
            SET name=?, opisanie=?, srok_podachi_date=?, result_date=?, level=?
            WHERE id = ?
        """, (name, opisanie, srok_podachi_date, result_date, level, event_id))
        conn.commit()
        flash('Конкурс успешно изменен', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception:
        flash('Ошибка при записи', 'error')
    finally:
        conn.close()


def delete_in_spisok(child_id):
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        # Проверяем, есть ли ребенок в студии
        cursor.execute('SELECT 1 FROM spisok_in_studio WHERE id_spisok = ?', (child_id,))
        if cursor.fetchone():
            flash('Нельзя удалить: ребенок числится в студии.', 'error')
            return
        # Проверяем участие в конкурсах
        cursor.execute('SELECT 1 FROM data_table WHERE id_spisok = ?', (child_id,))
        if cursor.fetchone():
            flash('Нельзя удалить: ребенок участвует в конкурсах.', 'error')
            return
        # Удаляем
        cursor.execute('DELETE FROM spisok WHERE id = ?', (child_id,))
        conn.commit()
        flash('Ребенок успешно удален', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception as e:
        flash(f'Ошибка при удалении: {e}', 'error')
    finally:
        conn.close()


def delete_in_spisok_in_studya(field_id):
    """Delete child from studio"""
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        # Check if child has competition records
        cursor.execute('SELECT 1 FROM data_table WHERE id_spisok_in_studio = ?', (field_id,))
        if cursor.fetchone():
            flash('Запись не может быть удалена, так как ребенок участвует в конкурсе.', 'error')
        else:
            cursor.execute('DELETE FROM spisok_in_studio WHERE id = ?', (field_id,))
            conn.commit()
            flash('Запись успешно удалена', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
    finally:
        conn.close()


def del_event(event_id):
    """Delete event"""
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        # Check if event has participants
        cursor.execute('SELECT 1 FROM data_table WHERE id_events_table = ?', (event_id,))
        if cursor.fetchone():
            flash('Запись не может быть удалена, так как есть дети, участвующие в этом конкурсе.', 'error')
        else:
            cursor.execute('DELETE FROM events_table WHERE id = ?', (event_id,))
            conn.commit()
            flash('Запись успешно удалена', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
    finally:
        conn.close()


def add_super_user():
    """Add admin user"""
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO teacher (FIO, password)
            VALUES (?, ?)
        """, ('admin', 'cdomir2024'))
        conn.commit()
    except Exception as e:
        flash(f'Ошибка при создании администратора: {e}', 'error')
    finally:
        conn.close()


def get_user_year_settings(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
             SELECT year_1, year_2 FROM user_settings
             WHERE user=?
             ORDER BY id DESC
             LIMIT 1
         """, (username,))
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        return 2024, 2025  # значения по умолчанию
    except Exception as e:
        flash(f'Ошибка получения настроек пользователя: {e}', 'error')
        return 2024, 2025
    finally:
        conn.close()


def set_user_year_settings(username, year_1, year_2):
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_settings (user, year_1, year_2)
            VALUES (?, ?, ?)
        """, (username, year_1, year_2))
        conn.commit()
    except Exception as e:
        flash(f'Ошибка установки настроек пользователя: {e}', 'error')
    finally:
        conn.close()


def delete_studya(studya_id):
    try:
        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        # Проверяем, используется ли студия
        cursor.execute('SELECT 1 FROM spisok_in_studio WHERE studio = ?', (studya_id,))
        if cursor.fetchone():
            flash('Нельзя удалить: студия используется.', 'error')
            return
        # Удаляем
        cursor.execute('DELETE FROM spr_studya WHERE id = ?', (studya_id,))
        conn.commit()
        flash('Студия успешно удалена', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Ошибка ссылочной целостности: {e}', 'error')
    except Exception as e:
        flash(f'Ошибка при удалении студии: {e}', 'error')
    finally:
        conn.close()