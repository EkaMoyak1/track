import sqlite3

from flask import flash

def check_user_credentials(username, password):
    # Ваша логика для проверки пользователя в базе данных
    # Например:

    conn = sqlite3.connect('date_source.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teacher WHERE fio=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def get_child_in_spisok(child_id):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("""
        SELECT 
        spisok.id,
        spisok.fio,
        spisok.date_bd,
        spisok.age
        FROM spisok 
        WHERE spisok.id = ?
    """, (child_id,))
    child = cursor_db.fetchone()
    cursor_db.close()
    db_lp.close()
    return child

def get_child_by_id(child_id):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("""
        SELECT 
        spisok.id,
        spisok.fio,
        spisok.date_bd,
        spisok.age,
        spisok_in_studio.id as id_table
        FROM spisok 
        join spisok_in_studio on spisok.id = spisok_in_studio.id_spisok  
        WHERE spisok.id = ?
    """, (child_id,))
    child = cursor_db.fetchone()
    cursor_db.close()
    db_lp.close()
    return child


def get_child_in_studya_by_id_copy(field_id):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("""
        SELECT 
            spisok.id,
            spisok.fio,
            spisok.date_bd,
            spisok.age,
            spisok_in_studio.napravlenie,
            spisok_in_studio.studio,
            spisok_in_studio.pedagog,
            spisok_in_studio.id as id_table
        FROM spisok_in_studio 
        JOIN spisok ON spisok_in_studio.id_spisok = spisok.id 
        WHERE spisok_in_studio.id = ?
    """, (field_id,))
    child = cursor_db.fetchone()
    cursor_db.close()
    db_lp.close()
    return child

def get_child_in_studya_by_id(field_id):

    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("""
        SELECT 
            spisok.id,
            spisok.fio,
            spisok.date_bd,
            spisok.age,
            spisok_in_studio.napravlenie,
            spisok_in_studio.studio,
            spisok_in_studio.pedagog,
            spisok_in_studio.id as id_table
        FROM spisok_in_studio 
        JOIN spisok ON spisok_in_studio.id_spisok = spisok.id 
        WHERE spisok_in_studio.id = ?
    """, (field_id,))
    child = cursor_db.fetchone()
    cursor_db.close()
    db_lp.close()
    return child

# Функция для получения данных о конкурсах по id_spisok
def get_data_by_id_spisok(id_spisok, id_spisok_in_st='', user='admin'):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    print(user, id_spisok)
    # cursor_db.execute("SELECT * FROM data_table  WHERE id_spisok = ?", (id_spisok,))
    if id_spisok_in_st=='':

        if user == 'admin':
            cursor_db.execute('''
                   SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                          events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file
                   FROM data_table
                   JOIN events_table ON data_table.id_events_table = events_table.id
                   WHERE data_table.id_spisok = ? 
                   ORDER BY data_table.id_spisok, events_table.result_date''', (id_spisok,))
        else:
            cursor_db.execute('''
                   SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                          events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file
                   FROM data_table
                   JOIN events_table ON data_table.id_events_table = events_table.id
                   
                   JOIN spisok_in_studio ON data_table.id_spisok_in_studio = spisok_in_studio.id
                   JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
                   
                   WHERE data_table.id_spisok = ? and teacher.fio = ? 
                   ORDER BY data_table.id_spisok, events_table.result_date''', (id_spisok, user))
    else:
        cursor_db.execute('''
               SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                      events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file
               FROM data_table
               JOIN events_table ON data_table.id_events_table = events_table.id
               JOIN spisok_in_studio ON spisok_in_studio.id_spisok = data_table.id_spisok
               WHERE data_table.id_spisok = ? and spisok_in_studio.id = ?
               ORDER BY data_table.id_spisok, events_table.result_date''', (id_spisok, id_spisok_in_st))
    data = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()

    return data


def get_data_by_id_spisok_kor(id_spisok, user):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()

    if user == 'admin':
        cursor_db.execute('''
                       SELECT events_table.name, data_table.id, data_table.result, data_table.id_spisok_in_studio 
                       FROM data_table
                       JOIN events_table ON data_table.id_events_table = events_table.id
                       WHERE data_table.id_spisok = ? 
                       ORDER BY events_table.result_date''', (id_spisok, ))
    else:
        cursor_db.execute('''
               SELECT events_table.name, data_table.id, data_table.result, data_table.id_spisok_in_studio 
               FROM data_table
               JOIN events_table ON data_table.id_events_table = events_table.id
               JOIN spisok_in_studio ON data_table.id_spisok_in_studio = spisok_in_studio.id
               JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
               WHERE data_table.id_spisok = ? and teacher.fio = ?
               ORDER BY events_table.result_date''', (id_spisok, user))
    data = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return data

def get_events_by_id(id):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM events_table  WHERE events_table.id = ?", (id,))
    events_table = cursor_db.fetchone()

    cursor_db.close()
    db_lp.close()

    return events_table


def get_events():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM events_table ORDER BY name ")
    events_table = cursor_db.fetchall()

    cursor_db.close()
    db_lp.close()
    events_table = [[f.replace('"', "") if type(f) == str else f for f in s] for s in events_table]

    return events_table

def get_child_by_spisok():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("""
        SELECT 
        spisok.id,
        spisok.fio,
        spisok.date_bd,
        spisok.age
        FROM spisok 
        ORDER BY spisok.fio
        """)
    child = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return child

def get_child_by_spisok_1(user, event):

    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    # cursor_db.execute("SELECT * FROM spisok  ORDER BY fio")
    if user == 'admin':
        text = '''
        SELECT spisok_in_studio.id, spisok.fio as fio, spisok.date_bd, spisok.age, spr_napravlenie.name, spr_studya.name, teacher.fio as pedagog, spisok.id 
        FROM data_table
        JOIN spisok_in_studio ON spisok_in_studio.id = data_table.id_spisok_in_studio  
        JOIN spisok ON spisok_in_studio.id_spisok = spisok.id
        left JOIN  spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
        left JOIN  spr_studya ON spisok_in_studio.studio = spr_studya.id
        left JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
        WHERE data_table.id_events_table = ?
        '''
        if filter:
            text += ' and spisok.id in (select id_spisok from data_table group by id_spisok) '

        cursor_db.execute(text + '''
        ORDER BY fio
        ''', (event,))
    else:
        text = '''
                SELECT spisok_in_studio.id, spisok.fio as fio, spisok.date_bd, spisok.age, spr_napravlenie.name, spr_studya.name, teacher.fio as pedagog, spisok.id 
                FROM data_table
                JOIN spisok_in_studio ON spisok_in_studio.id = data_table.id_spisok_in_studio 
                JOIN spisok ON spisok_in_studio.id_spisok = spisok.id
                left JOIN  spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
                left JOIN  spr_studya ON spisok_in_studio.studio = spr_studya.id
                JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
                WHERE data_table.id_events_table = ? and teacher.fio = ?
                '''
        if filter:
            text += ' and  spisok.id in (select id_spisok from data_table group by id_spisok) '

        cursor_db.execute( text + '''  
             ORDER BY fio''', (event,user))
    children = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return children

# список для карты мршрута по spisok

def get_children_in_spisok(user, filter=False):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    if user == 'admin':
        text = '''
        SELECT spisok_in_studio.id, spisok.fio as fio, spisok.date_bd, spisok.age, spr_napravlenie.name, spr_studya.name, teacher.fio as pedagog, spisok.id 
        FROM spisok  
        JOIN spisok_in_studio ON spisok_in_studio.id_spisok = spisok.id
        left JOIN  spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
        left JOIN  spr_studya ON spisok_in_studio.studio = spr_studya.id
        left JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
        '''
        if filter:
            text += ' where spisok.id in (select id_spisok from data_table group by id_spisok) '

        cursor_db.execute(text + '''
        ORDER BY fio
        ''')
    else:
        text = '''
                SELECT spisok_in_studio.id, spisok.fio as fio, spisok.date_bd, spisok.age, spr_napravlenie.name, spr_studya.name, teacher.fio as pedagog, spisok.id 
                FROM spisok  
                left JOIN spisok_in_studio ON spisok_in_studio.id_spisok = spisok.id
                left JOIN  spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
                left JOIN  spr_studya ON spisok_in_studio.studio = spr_studya.id
                JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
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

# список для карты мршрута

def get_children(user, filter=False):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    # cursor_db.execute("SELECT * FROM spisok  ORDER BY fio")
    if user == 'admin':
        text = '''
        SELECT spisok_in_studio.id, spisok.fio as fio, spisok.date_bd, spisok.age, spr_napravlenie.name, spr_studya.name, teacher.fio as pedagog, spisok.id 
        FROM spisok  
        JOIN spisok_in_studio ON spisok_in_studio.id_spisok = spisok.id
        left JOIN  spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
        left JOIN  spr_studya ON spisok_in_studio.studio = spr_studya.id
        left JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
        '''
        if filter:
            text += ' where spisok.id in (select id_spisok from data_table group by id_spisok) '

        cursor_db.execute(text + '''
        ORDER BY fio
        ''')
    else:
        text = '''
                SELECT spisok_in_studio.id, spisok.fio as fio, spisok.date_bd, spisok.age, spr_napravlenie.name, spr_studya.name, teacher.fio as pedagog, spisok.id 
                FROM spisok  
                left JOIN spisok_in_studio ON spisok_in_studio.id_spisok = spisok.id
                left JOIN  spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
                left JOIN  spr_studya ON spisok_in_studio.studio = spr_studya.id
                JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
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

def get_children_group(user, filter=False):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    # cursor_db.execute("SELECT * FROM spisok  ORDER BY fio")
    if user == 'admin':
        text = '''
        SELECT 
        max(spisok_in_studio.id), 
        spisok.fio as fio, 
        max(spisok.date_bd), 
        max(spisok.age), 
        max(spr_napravlenie.name), 
        max(spr_studya.name), 
        max(teacher.fio) as pedagog, 
        spisok.id 
        FROM spisok  
        JOIN spisok_in_studio ON spisok_in_studio.id_spisok = spisok.id
        left JOIN  spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
        left JOIN  spr_studya ON spisok_in_studio.studio = spr_studya.id
        left JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
        '''
        if filter:
            text += ' where spisok.id in (select id_spisok from data_table group by id_spisok) '

        cursor_db.execute(text + '''
        GROUP BY spisok.fio, spisok.id
        ORDER BY fio
        ''')
    else:
        text = '''
                SELECT 
                max(spisok_in_studio.id), 
                spisok.fio as fio, 
                max(spisok.date_bd), 
                max(spisok.age), 
                max(spr_napravlenie.name), 
                max(spr_studya.name), 
                teacher.fio as pedagog, 
                spisok.id 
                FROM spisok  
                left JOIN spisok_in_studio ON spisok_in_studio.id_spisok = spisok.id
                left JOIN  spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
                left JOIN  spr_studya ON spisok_in_studio.studio = spr_studya.id
                JOIN  teacher ON spisok_in_studio.pedagog = teacher.id
                WHERE teacher.fio = ?
                '''
        if filter:
            text += ' and  spisok.id in (select id_spisok from data_table group by id_spisok) '

        cursor_db.execute( text + ''' 
             GROUP BY spisok.fio, spisok.id, teacher.fio 
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

def get_teacher(user_name=None):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    if user_name == 'admin' or user_name == None:
        cursor_db.execute("SELECT * FROM teacher where fio <> 'admin'")
    else:
        cursor_db.execute("SELECT * FROM teacher where fio = ?", (user_name,))

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
        field_id = request.form['field_id']
        file = request.files['fileInput']
        original_name = file.filename
        ext = original_name.split('.')[-1]
        saved_file_name += '.' + ext
        print(field_id)

        # Сохранение данных в базе данных
        db_lp = sqlite3.connect('date_source.db')
        cursor_db = db_lp.cursor()
        cursor_db.execute("INSERT INTO data_table (id_spisok, id_spisok_in_studio, id_events_table, result, original_name, file) VALUES (?, ?, ?, ?, ?, ?)",
                          (id_spisok, field_id, id_events_table, doc_type, original_name, saved_file_name))
        db_lp.commit()
        cursor_db.close()
        db_lp.close()
        flash('Запись успешно добавлена', 'success')
    except KeyError as e:
        flash(f'Ошибка: отсутствует поле {e}', 'error')


def update_in_data_table(request):
    record_id = request.form.get('record-id')
    id_spisok = request.form.get('id_spisok')
    id_events_table = request.form.get('id_events_table')
    result = request.form.get('id_doc_type')
    file = request.form.get('saved_file_name')
    original_name = request.form.get('original_file_name')


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
        flash('Запись успешно изменена', 'success')
    except KeyError as e:
        flash(f'Ошибка: отсутствует поле {e}', 'error')


def delete_in_data_table(record_id):
    try:
        # Подключение кбазе данных и вставка данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()
        cursor.execute('DELETE FROM data_table WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        flash('Запись успешно удалена', 'success')
    except KeyError as e:

        flash(f'Ошибка: отсутствует поле {e}', 'error')


def add_in_spisok_in_studio(request):
    id_ch = request.form['fio']
    napravlenie = request.form['id_napr_table']
    studio = request.form['id_studio']
    pedagog = request.form['id_teacher']

    # Логика добавления ребенка в базу данных
    conn = sqlite3.connect('date_source.db')

    cursor = conn.cursor()
    cursor.execute('INSERT INTO spisok_in_studio (id_spisok, napravlenie, studio, pedagog) VALUES (?, ?, ?, ?)',
                   (id_ch, napravlenie, studio, pedagog))

    # Получение ID только что добавленной записи
    id_spisok = cursor.lastrowid

    conn.commit()
    conn.close()


def add_in_spisok(request):
    fio = request.form['fio1']
    date_bd = request.form['date_bd']
    age = request.form['age']

    # Логика добавления ребенка в базу данных
    conn = sqlite3.connect('date_source.db')

    cursor = conn.cursor()
    cursor.execute('INSERT INTO spisok (fio, date_bd, age) VALUES (?, ?, ?)',
                   (fio, date_bd, age))

    conn.commit()
    conn.close()
    return {'fio':fio, 'dr':date_bd, 'age':age}



def add_in_event(request):

    name = request.form['name']
    opisanie = request.form['opisanie']
    srock = request.form['srock']
    resultat_date = request.form['resultat_date']

    try:
        # Логика добавления конкурса в базу данных
        conn = sqlite3.connect('date_source.db')
        cursor = conn.cursor()
        cursor.execute('''
                    INSERT INTO events_table (name, opisanie, srok_podachi_date, result_date)
                    VALUES (?, ?, ?, ?)
                ''', (name, opisanie, srock, resultat_date))
        conn.commit()
        conn.close()
        txt = 'Конкурс успешно добавлен'
        flash(txt, 'success')
        return {"result": True}
    except:
        conn.close()
        txt = 'Ошибка при записи конкурса'
        flash(txt, 'error')
        return {"result": False}


def edit_in_spisok(request, child_id):
    try:
        date_bd = request.form['date_bd']
        age = request.form['age']
        fio = request.form['fio']

        # Логика для обновления данных ребенка
        conn = sqlite3.connect('date_source.db')
        cursor = conn.cursor()
        cursor.execute('''
                            UPDATE spisok
                            SET date_bd=?, age=?, fio=? 
                            where id = ?
                    ''', (date_bd, age, fio, child_id))
        conn.commit()
        conn.close()
        txt = 'Ребенок успешно изменен'
        flash(txt, 'success')
    except:
        txt = 'Ошибка при записи'
        flash(txt, 'success')


def edit_in_spisok_studya(request, field_id):
    try:
        date_bd = request.form['date_bd']
        age = request.form['age']
        napravlenie = request.form['id_napr_table']
        studio = request.form['id_studio']
        pedagog = request.form['id_teacher']

        spis = get_child_in_studya_by_id(field_id)
        child_id = spis[0]

        # Логика для обновления данных ребенка
        conn = sqlite3.connect('date_source.db')

        cursor = conn.cursor()
        cursor.execute('''
                            UPDATE spisok
                            SET date_bd=?, age=?
                            where id = ?
                    ''', (date_bd, age, child_id))
        conn.commit()

        cursor = conn.cursor()
        cursor.execute('''
                                UPDATE spisok_in_studio
                                SET napravlenie=?, studio=?, pedagog=?
                                where id = ?
                        ''', (napravlenie, studio, pedagog,  field_id))
        conn.commit()

        conn.close()
        txt = 'Ребенок успешно изменен'
        flash(txt, 'success')
    except:
        txt = 'Ошибка при записи'
        flash(txt, 'success')



def edit_in_events(request, id):
    try:
        name = request.form['name']
        opisanie = request.form['opisanie']
        srok_podachi_date = request.form['srok_podachi_date']
        result_date = request.form['result_date']

        # Логика для обновления данных ребенка
        conn = sqlite3.connect('date_source.db')
        cursor = conn.cursor()
        cursor.execute('''
                            UPDATE events_table
                            SET name=?, opisanie=?, srok_podachi_date=?, result_date=? 
                            where id = ?
                    ''', (name, opisanie, srok_podachi_date, result_date, id))
        conn.commit()
        conn.close()
        txt = 'Конкурс успешно изменен'
        flash(txt, 'success')
    except:
        txt = 'Ошибка при записи'
        flash(txt, 'success')


def delete_in_spisok(child_id):
    try:
        # Подключение к базе данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()

        # Проверка наличия ключа в таблице spisok_in_studio
        cursor.execute('SELECT 1 FROM spisok_in_studio WHERE id_spisok = ?', (child_id,))
        record_exists = cursor.fetchone()

        if record_exists:
            txt = 'Запись не может быть удалена, так как ребенок числится в студии.'

            flash(txt, 'error')
        else:
            # Удаление записи из таблицы spisok
            cursor.execute('DELETE FROM spisok WHERE id = ?', (child_id,))
            conn.commit()
            txt = 'Запись успешно удалена'
            flash(txt, 'success')

    except KeyError as e:
        txt ='Ошибка: отсутствует поле ' + str(e)
        flash(f'Ошибка: отсутствует поле {e}', 'error')

    except sqlite3.Error as e:
        txt ='Ошибка базы данных: '+ str(e)
        flash(f'Ошибка базы данных: {e}', 'error')
    finally:
        # Закрытие соединения с базой данных
        conn.close()

    return txt

def delete_in_spisok_in_studya(field_id):
    try:
        # Подключение кбазе данных и вставка данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()

        # Проверка наличия ключа в таблице data_table
        cursor.execute('SELECT 1 FROM data_table WHERE id_spisok = ?', (field_id,))
        record_exists = cursor.fetchone()

        if record_exists:
            txt = 'Запись не может быть удалена, так как ребенок  участвует в конкурсе.'
            flash(txt, 'error')
        else:
            cursor.execute('DELETE FROM spisok_in_studio WHERE id = ?', (field_id,))
            conn.commit()
            flash('Запись успешно удалена', 'success')
        conn.close()

    except KeyError as e:
        flash(f'Ошибка: {e}', 'error')

def del_event(field_id):
    try:
        # Подключение к базе данных и вставка данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()

        # Проверка наличия ключа в таблице data_table
        cursor.execute('SELECT 1 FROM data_table WHERE id_events_table = ?', (field_id,))
        record_exists = cursor.fetchone()

        if record_exists:
            txt = 'Запись не может быть удалена, так как есть дети, участвующие в этом конкурсе.'
            flash(txt, 'error')
        else:
            cursor.execute('DELETE FROM events_table WHERE id = ?', (field_id,))
            conn.commit()
            flash('Запись успешно удалена', 'success')
        conn.close()

    except KeyError as e:
        flash(f'Ошибка: {e}', 'error')


def add_super_user():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute('''
                    INSERT INTO teacher (FIO, password)
                    VALUES (?, ?)
                ''', ('admin', 'cdomir2024'))

    # Сохранение изменений в базе данных
    db_lp.commit()