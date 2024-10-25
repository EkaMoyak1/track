import sqlite3

from flask import flash

def check_user_credentials(username, password):
    # Ваша логика для проверки пользователя в базе данных
    # Например:
    print(username, password)
    conn = sqlite3.connect('date_source.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teacher WHERE fio=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_child_by_id(child_id):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM spisok WHERE id = ?", (child_id,))
    child = cursor_db.fetchone()
    cursor_db.close()
    db_lp.close()
    return child


# Функция для получения данных о конкурсах по id_spisok
def get_data_by_id_spisok(id_spisok):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    # cursor_db.execute("SELECT * FROM data_table  WHERE id_spisok = ?", (id_spisok,))
    cursor_db.execute('''
           SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                  events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file
           FROM data_table
           JOIN events_table ON data_table.id_events_table = events_table.id
           WHERE data_table.id_spisok = ?
           ORDER BY data_table.id_spisok, events_table.result_date''', (id_spisok,))
    data = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()

    return data


def get_data_by_id_spisok_kor(id_spisok):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()

    cursor_db.execute('''
           SELECT events_table.name, data_table.id, data_table.result 
           FROM data_table
           JOIN events_table ON data_table.id_events_table = events_table.id
           WHERE data_table.id_spisok = ?
           ORDER BY events_table.result_date''', (id_spisok,))
    data = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return data


def get_events():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM events_table ORDER BY result_date ")
    events_table = cursor_db.fetchall()

    cursor_db.close()
    db_lp.close()
    events_table = [[f.replace('"', "") if type(f) == str else f for f in s] for s in events_table]

    return events_table


def get_children(user, filter=False):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    # cursor_db.execute("SELECT * FROM spisok  ORDER BY fio")
    if user == 'admin':
        text = '''
        SELECT spisok.id, spisok.fio as fio, spisok.date_bd, spisok.age, spr_napravlenie.name, spr_studya.name, teacher.fio as pedagog 
        FROM spisok  
        left JOIN  spr_napravlenie ON spisok.napravlenie = spr_napravlenie.id
        left JOIN  spr_studya ON spisok.studio = spr_studya.id
        left JOIN  teacher ON spisok.pedagog = teacher.id
        '''
        if filter:
            text += ' where spisok.id in (select id_spisok from data_table group by id_spisok) '

        cursor_db.execute(text + '''
        ORDER BY fio
        ''')
    else:
        text = '''
                SELECT spisok.id, spisok.fio as fio, spisok.date_bd, spisok.age, spr_napravlenie.name, spr_studya.name, teacher.fio as pedagog 
                FROM spisok  
                left JOIN  spr_napravlenie ON spisok.napravlenie = spr_napravlenie.id
                left JOIN  spr_studya ON spisok.studio = spr_studya.id
                JOIN  teacher ON spisok.pedagog = teacher.id
                WHERE teacher.fio = ?
                '''
        if filter:
            text += ' and  spisok.id in (select id_spisok from data_table group by id_spisok) '

        cursor_db.execute( text + '''  
             ORDER BY fio''', (user,))
    children = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return children


def get_napr():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM spr_napravlenie")

    napr_spr = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return napr_spr


def get_siudio():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM spr_studya")

    spr_studya = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return spr_studya

def get_teacher():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM teacher where fio <> 'admin'")

    teacher = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return teacher

# сохранение данных

def save_in_date_table(request):
    try:
        id_spisok = request.form['id_spisok']
        id_events_table = request.form['id_events_table']
        doc_type = request.form['doc_type']
        saved_file_name = request.form['saved_file_name']
        file = request.files['fileInput']
        original_name = file.filename

        ext = original_name.split('.')[-1]
        saved_file_name += '.' + ext

        # Сохранение данных в базе данных
        db_lp = sqlite3.connect('date_source.db')
        cursor_db = db_lp.cursor()
        cursor_db.execute("INSERT INTO data_table (id_spisok, id_events_table, result, original_name, file) VALUES (?, ?, ?, ?, ?)",
                          (id_spisok, id_events_table, doc_type, original_name, saved_file_name))
        db_lp.commit()
        cursor_db.close()
        db_lp.close()
        print('Запись успешно добавлена')
        # flash('Запись успешно добавлена', 'success')
    except KeyError as e:
        print('error')
        flash(f'Ошибка: отсутствует поле {e}', 'error')


def update_in_data_table(request):
    record_id = request.form.get('record-id')
    id_spisok = request.form.get('id_spisok')
    id_events_table = request.form.get('id_events_table')
    result = request.form.get('id_doc_type')
    file = request.form.get('saved_file_name')
    original_name = request.form.get('original_file_name')
    print(original_name, file)

    try:
        # Подключение кбазе данных и вставка данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()
        if original_name == '' or original_name == None:
            cursor.execute('''UPDATE data_table
                                      SET id_spisok = ?, id_events_table = ?, result = ?
                                      WHERE id = ?''',
                           (id_spisok, id_events_table, result, record_id))
        else:
            cursor.execute('''UPDATE data_table
                          SET id_spisok = ?, id_events_table = ?, result = ?, file = ?, original_name = ?
                          WHERE id = ?''', (id_spisok, id_events_table, result, file, original_name,  record_id))
        conn.commit()
        conn.close()
        print('Запись успешно изменена')
        flash('Запись успешно изменена', 'success')
    except KeyError as e:
        print('error')
        flash(f'Ошибка: отсутствует поле {e}', 'error')


def delete_in_data_table(record_id):
    try:
        # Подключение кбазе данных и вставка данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()
        cursor.execute('DELETE FROM data_table WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        print('Запись успешно удалена')
        flash('Запись успешно удалена', 'success')
    except KeyError as e:
        print('error')
        flash(f'Ошибка: отсутствует поле {e}', 'error')


def add_in_spisok(request):
    fio = request.form['fio']
    date_bd = request.form['date_bd']
    age = request.form['age']
    napravlenie = request.form['id_napr_table']
    studio = request.form['id_studio']
    pedagog = request.form['id_teacher']

    # Логика добавления ребенка в базу данных
    conn = sqlite3.connect('date_source.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO spisok (fio, date_bd, age, napravlenie, studio, pedagog) VALUES (?, ?, ?, ?, ?, ?)',
                   (fio, date_bd, age, napravlenie, studio, pedagog))
    conn.commit()
    conn.close()


def add_in_event(request):
    name = request.form['name']
    opisanie = request.form['opisanie']
    srock = request.form['srock']
    resultat_date = request.form['resultat_date']


    # Логика добавления конкурса в базу данных
    conn = sqlite3.connect('date_source.db')
    cursor = conn.cursor()
    cursor.execute('''
                INSERT INTO events_table (name, opisanie, srok_podachi_date, result_date)
                VALUES (?, ?, ?, ?)
            ''', (name, opisanie, srock, resultat_date))
    conn.commit()
    conn.close()

def edit_in_spisok(request, child_id):
    date_bd = request.form['date_bd']
    age = request.form['age']
    napravlenie = request.form['id_napr_table']
    studio = request.form['id_studio']
    pedagog = request.form['id_teacher']

    # Логика для обновления данных ребенка
    conn = sqlite3.connect('date_source.db')
    cursor = conn.cursor()
    cursor.execute('''
                        UPDATE spisok
                        SET date_bd=?, age=?, napravlenie=?, studio=?, pedagog=? 
                        where id = ?
                ''', (date_bd, age, napravlenie, studio, pedagog, child_id))
    conn.commit()
    conn.close()


def delete_in_spisok(child_id):
    try:
        # Подключение кбазе данных и вставка данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()
        cursor.execute('DELETE FROM spisok WHERE id = ?', (child_id,))
        conn.commit()
        conn.close()
        print('Запись успешно удалена')
        flash('Запись успешно удалена', 'success')
    except KeyError as e:
        print('error')
        flash(f'Ошибка: отсутствует поле {e}', 'error')


def add_super_user():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute('''
                    INSERT INTO teacher (FIO, password)
                    VALUES (?, ?)
                ''', ('admin', 'cdomir2024'))

    # Сохранение изменений в базе данных
    db_lp.commit()