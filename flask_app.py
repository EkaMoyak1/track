
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask import session
import json
import pandas as pd
import io
import load_data, files
import os
from sql_utils import *
import sqlite3
from functools import wraps
from datetime import datetime  # ✅ Правильный вариант
import zipfile

app = Flask(__name__)

# Установите секретный ключ
app.secret_key = os.urandom(24)

docs =[' ', 'Сертификат участника',
        'Диплом 1 степени',
        'Диплом 2 степени',
        'Диплом 3 степени',
        'Диплом финалиста',
        'Лауреат',
        'Лауреат 1 степени',
        'Лауреат 2 степени',
        'Лауреат 3 cтепени']

levels = [' ', 'Центровский', 'Городской', 'Районный', 'Республиканский', 'Региональный', 'Межрегиональный', 'Всероссийский', 'Международный']
# Функция для получения данных о конкретном ребенке по ID
setup_db()
app.secret_key = os.urandom(24)

@app.before_request
def before_request():
    if 'username' not in session and request.endpoint not in ['login', 'static']:
        return redirect(url_for('login'))

    if 'username' in session and request.endpoint not in ['login', 'static']:
        username = session['username']
        year_1, year_2 = get_user_year_settings(username)
        session['year_1'] = year_1
        session['year_2'] = year_2
        session.modified = True

@app.route('/protected')
def protected():
    if 'username' in session:
        return 'Вы вошли как ' + session['username']
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Здесь должна быть проверка логина и пароля
        # Например, сравнить с данными в базе данных
        if check_user_credentials(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/')
def index():
    children = get_children(session['username'])
    return render_template('index.html', children=children)

# первичная загрузка
@app.route('/load')
def load_data_route():
    load_data.load_data()  # Предполагается, что у вас есть функция load_data в load_data.py
    return redirect(url_for('index'))  # После завершения загрузки перенаправим на главную страницу

# Дозагрузка списка детей
@app.route('/load_add')
def load_add():
    load_data.load_data_add()  # Предполагается, что у вас есть функция load_data в load_data.py
    return redirect(url_for('index'))  # После завершения загрузки перенаправим на главную страницу


@app.route('/spisok')
def spisok():
    if session['username'] == 'admin':
        show_load_button = True
    else:
        show_load_button = False
    children = get_children(session['username'])  # Получаем список детей из базы данных
    return render_template('spisok.html', children=children, show_load_button=show_load_button)

# СПИСОК детей в конкурсе
@app.route('/spisok_in_event/<int:event_id>')
def spisok_in_event(event_id):
    # Получаем информацию о конкурсе
    event = get_events_by_id(event_id)

    # Получаем участников конкурса
    children = get_children_list_from_event(session['username'], event_id=event_id)


    return render_template(
        'spisok_event.html',
        event_name=event['name'],
        event_id=event_id,
        children=children,
        docs=docs)

@app.route('/available_children')
def available_children():
    user = session.get('username')
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'}), 401

    children = get_children_list(user)

    result = []
    for child in children:
        if isinstance(child, sqlite3.Row):
            child = dict(child)  # Преобразуем Row в словарь

        result.append({
            'id': child.get('id_in_studya'),
            'fio': child.get('fio'),
            'studya': child.get('studya'),
            'pedagog': child.get('pedagog'),
            'id_spisok': child.get('id_in_spisok')

        })
        #print(result)

    return jsonify(result)


@app.route('/event/<int:event_id>/add', methods=['POST'])
def add_to_event(event_id):
    if request.method != 'POST':
        return jsonify({'success': False, 'message': 'Метод не поддерживается'}), 405

    try:
        data = request.get_json()
        children_ids = data.get('children', [])
        # print(data)
        # print(children_ids)

        if not children_ids:
            return jsonify({'success': False, 'message': 'Не выбран ни один участник'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли конкурс
        cursor.execute("SELECT 1 FROM events_table WHERE id = ?", (event_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Конкурс не найден'}), 404
        # print(event_id)
        added_count = 0
        for child_id in children_ids:
            # Проверяем, существует ли ребенок и получаем id_spisok
            cursor.execute("SELECT id_spisok FROM spisok_in_studio WHERE id = ?", (child_id,))
            child_data = cursor.fetchone()
            if not child_data:
                print(f"Ребенок {child_id} не существует")
                continue  # Пропускаем несуществующих детей


            id_spisok = child_data[0]

            # Проверяем, не добавлен ли уже ребенок в этот конкурс
            cursor.execute("""
                SELECT 1 FROM data_table 
                WHERE id_spisok_in_studio = ? AND id_events_table = ?
            """, (child_id, event_id))
            if cursor.fetchone():
                print("Ребенок уже участвует в этом конкурсе")
                continue  # Ребенок уже участвует в этом конкурсе

            # Добавляем запись в data_table
            cursor.execute("""
                INSERT INTO data_table (id_spisok, id_spisok_in_studio, id_events_table)
                VALUES (?, ?, ?)
            """, (id_spisok, child_id, event_id))

            added_count += 1
            print(f"Добавлен участник {id_spisok} ребенок {child_id} в конкурс {event_id}")

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'added': added_count,
            'message': f'Успешно добавлено {added_count} участников'
        })

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'message': f'Ошибка при добавлении: {str(e)}'}), 500


# Удаление участника из конкурса
@app.route('/event/<int:event_id>/remove/<int:id>')
def remove_from_event(event_id, id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM data_table 
            WHERE id = ? 
        """, (id,))
        conn.commit()
        conn.close()
        flash('Участник удален из конкурса', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    return redirect(url_for('spisok_in_event', event_id=event_id))


@app.route('/karta')
def karta():
    user = session['username']
    #нужно получить список по spisok
    children = (get_children_group(user, True))  # Получаем список детей из базы данных
    table_res = []

    for child in children:
        ## по ключу ребенка
        ev = get_data_by_id_spisok_kor(child[7], user)
        if ev:
            table_res.append([child[1],list(ev), child[0]])


    return render_template('children_profiles.html', children=table_res)



@app.route('/child/<int:child_id>')
def child_profile(child_id):
    # child = get_child_by_id(child_id)

    child = get_child_in_studya_by_id(child_id)

    if child:
        # data = get_data_by_id_spisok(child_id, user=session['username'])
        data = get_data_by_id_spisok(child['id'], user=session['username'])
        events = get_events()
        return render_template('child_profile.html', events = events, child=child, data=data, docs=docs)
    return "Ребенок не найден", 404


## --------------- Работа с маршрутом --------------------##

# Настройте папку для загрузки файлов
UPLOAD_FOLDER = 'load'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# #Добавление записи об участии в мероприятии
# @app.route('/add_data_entry/<int:child_id>', methods=['GET', 'POST'])
# def add_data_entry(child_id):
#     # child = get_child_by_id(child_id)  # Получаем информацию о ребенке по ID
#     child = get_child_in_studya_by_id(child_id)
#
#     if request.method == 'GET':
#         # Получите данные детей и конкурсов из БД
#         children = get_children(session['username'])  # Ваша функция для получения детей
#
#         events = get_events()  # Ваша функция для получения конкурсов
#
#         return render_template('edit_field.html', child = child, children=children, events=events, docs=docs, id_child=child_id)
#        # Обработка POST запроса здесь
#     elif request.method == 'POST':
#         # id_spisok = request.form['id_spisok']
#         save_in_date_table(request)
#         return redirect(url_for('child_profile', child_id = child_id))


#Добавление записи об участии в мероприятии
@app.route('/add_data_entry/<int:child_id>', methods=['GET'])
def add_data_entry(child_id):
    # child = get_child_by_id(child_id)  # Получаем информацию о ребенке по ID
    child = get_child_in_studya_by_id(child_id)


    # Получите данные детей и конкурсов из БД
    children = get_children(session['username'])  # Ваша функция для получения детей

    events = get_events()  # Ваша функция для получения конкурсов

    return render_template('edit_field.html', child = child, children=children, events=events, docs=docs, id_child=child_id)
   # Обработка POST запроса здесь



@app.route('/save_data_ajax', methods=['POST'])
def save_data_ajax():
    try:
        id_spisok = request.form.get('id_spisok')
        field_id = request.form.get('field_id')
        id_events_table = request.form.get('id_events_table')
        doc_type = request.form.get('doc_type')
        date_otcheta = request.form.get('date_otcheta')

        file = request.files.get('fileInput')
        saved_file_name = request.form.get('saved_file_name')

        original_name = ''
        full_file_name = ''

        if file and file.filename:
            original_name = file.filename
            ext = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else 'bin'
            full_file_name = f"{saved_file_name}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], full_file_name))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO data_table 
            (id_spisok, id_spisok_in_studio, id_events_table, result, original_name, file, date_otcheta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_spisok, field_id, id_events_table, doc_type, original_name, full_file_name, date_otcheta))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Запись успешно добавлена'})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/upload_result', methods=['POST'])
def upload_result():
    try:
        record_id = request.form.get('record_id')
        doc_type = request.form.get('doc_type')
        date_otcheta = request.form.get('date_otcheta')  # Новое поле

        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем текущую запись для проверки старого имени файла
        cursor.execute("SELECT file FROM data_table WHERE id = ?", (record_id,))
        old_record = cursor.fetchone()
        old_file_name = old_record['file'] if old_record else None
        new_date = date_otcheta  # Сохраняем дату из формы

        original_name = ''
        file_name = old_file_name  # Сохраняем старое имя, если файл не загружен

        # Если загружен новый файл
        if 'fileInput' in request.files and request.files['fileInput'].filename:
            file = request.files['fileInput']
            original_name = file.filename
            ext = original_name.rsplit('.', 1)[-1] if '.' in original_name else 'bin'
            file_name = f"{request.form.get('saved_file_name')}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        elif not old_file_name:
            # Если файла раньше не было и сейчас тоже нет — можно оставить пустым или установить NULL
            file_name = None

        # Обновляем запись
        cursor.execute("""
            UPDATE data_table 
            SET result = ?, original_name = ?, file = ?, date_otcheta = ?
            WHERE id = ?
        """, (doc_type, original_name, file_name, new_date, record_id))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Запись не найдена'}), 404

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Файл загружен и запись обновлена'})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


#загрузка файла
@app.route('/upload_file', methods=['POST'])
def upload_file():
    # Обработка загрузки файла
    file_name = request.form.get('saved_file_name')
    # print(file_name)

    # Проверяем наличие файла
    if 'fileInput' not in request.files:
        return "Нет файла", 400

    file = request.files['fileInput']

    if file.filename == '':
        return "Файл не выбран", 400

    original_name = file.filename
    ext = original_name.split('.')[-1]
    file_name += '.' + ext
    # Сохраняем файл в папку load
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
    return   jsonify({'saved_file_name': file_name, 'file_name': file.filename}), 200


@app.route('/remove_file/<int:record_id>', methods=['POST'])
def remove_file(record_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем текущую запись
        cursor.execute("SELECT original_name, file FROM data_table WHERE id = ?", (record_id,))
        record = cursor.fetchone()
        if not record:
            return jsonify({'success': False, 'message': 'Запись не найдена'}), 404

        # Сохраняем имя файла, чтобы удалить его с диска
        old_filename = record['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename) if old_filename else None

        # Обновляем запись: ставим NULL вместо ''
        cursor.execute("""
            UPDATE data_table 
            SET result = '', original_name = NULL, file = NULL 
            WHERE id = ?
        """, (record_id,))
        conn.commit()

        # Удаляем файл с диска, если он был
        if old_filename and os.path.exists(file_path):
            os.remove(file_path)

        conn.close()
        return jsonify({'success': True, 'message': 'Файл удален из записи'})
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500


# запись в базу об участии в конкурсе
@app.route('/save_data', methods=['POST'])
def save_data():

    id_spisok = request.form.get('id_spisok')

    if request.method =='POST':
        print(1)
        update_in_data_table(request)

    return jsonify({'status': 'success'})  # Возвращаем JSON-ответ



@app.route('/delete_data', methods=['POST'])
def delete_data():
    record_id = request.form.get('record_id')
    delete_in_data_table(record_id)
    return jsonify({'status': 'success'})

## ------------- Работа со справочником детей --------- ##

# СПИСОК ВСЕХ ДЕТЕЙ (БЕЗ ПРИВЯЗКИ К СТУДИЯМ)
@app.route('/spisok_children')
def spisok_children():
    if session['username'] == 'admin':
        show_load_button = True
    else:
        show_load_button = False
    children = get_children_list_simple() # Получаем список детей из базы данных
    return render_template('spisok_children.html', children=children, show_load_button=show_load_button, result="")



## ДОБАВЛЕНИЕ ОТСУТСТВУЮЩЕГО РЕБЕНКА
@app.route('/add_child_in_spisok', methods=['GET', 'POST'])
def add_child_in_spisok():
    if request.method == 'POST':
        resp = add_in_spisok(request)
        # Получите обновленный список детей
        children = get_children_list_simple()

        resp['children'] = children
        return json.dumps(resp, ensure_ascii=False, indent=4)
    else:
        return redirect(url_for('spisok_children'))


## ДОБАВЛЕНИЕ ОТСУТСТВУЮЩЕГО РЕБЕНКА
@app.route('/add_child_in_spisok_1', methods=['GET', 'POST'])
def add_child_in_spisok_1():
    if request.method == 'POST':
        resp = add_in_spisok(request)
        # # Получите обновленный список детей
        # children = get_child_by_spisok()

        return redirect(url_for('spisok_children'))
    else:
        return redirect(url_for('spisok_children'))

@app.route('/add_child_in_spisok_2', methods=['GET', 'POST'])
def add_child_in_spisok_2():
    if request.method == 'POST':
        resp = add_in_spisok(request)
        return redirect(url_for('add_child_in_spisok_2'))
    else:
        return redirect(url_for('add_child_in_spisok_2'))

## УДАЛЕНИЕ РЕБЕНКА ИЗ ОБЩЕГО СПИСКА
@app.route('/delete_child_in_spisok/<int:child_id>', methods=['GET', 'POST'])
def delete_child_in_spisok(child_id):

    result = delete_in_spisok(child_id)
    children = get_children_list_simple()
    return render_template('spisok_children.html', children=children, show_load_button=False, result=result)

## РЕДАКТИРОВАНИЕ  РЕБЕНКА В СПИСКЕ
@app.route('/edit_child_in_spisok/<int:child_id>', methods=['GET', 'POST'])
def edit_child_in_spisok(child_id):
    child = get_child_in_spisok(child_id)
    if request.method == 'POST':
        edit_in_spisok(request, child_id)
        return redirect(url_for('spisok_children'))
    else:
        return render_template('edit_child_in_spisok.html', child=child)  #


## ------------- Работа со справочником детей в студиях  --------- ##

## ДОБАВЛЕНИЕ РЕБЕНКА В СТУДИЮ
@app.route('/add_child', methods=['GET', 'POST'])
def add_child():
    if request.method == 'POST':
        add_in_spisok_in_studio(request)
        # children = get_children(session['username'])  # Получаем список детей из базы данных
        return redirect(url_for('spisok'))
    napr_table = get_napr()
    spr_studya = get_siudio()
    teacher = get_teacher(session['username'])
    children = get_child_by_spisok()
    return render_template('add_child.html', napr_table=napr_table, spr_studya=spr_studya, teacher=teacher, children=children)  # Создайте этот шаблон

## КОРРЕКТИРОВКА РЕБЕНКА В СТУДИЮ
@app.route('/edit_child/<int:child_id>', methods=['GET', 'POST'])
def edit_child(child_id):
    # child = get_child_by_id(child_id)
    child = get_child_in_studya_by_id(child_id)
    if request.method == 'POST':
        # fio = request.form['fio']
        # edit_in_spisok(request, child_id)
        edit_in_spisok_studya(request, child_id)
        children = get_children(session['username'])  # Получаем список детей из базы данных
        # return render_template('spisok.html', children=children, show_load_button=False)
        return redirect(url_for('spisok'))

    else:
        napr_table = get_napr()
        spr_studya = get_siudio()
        teacher = get_teacher()
        return render_template('edit_child.html', child=child, napr_table=napr_table, spr_studya=spr_studya, teacher=teacher)  #

## УДАЛЕНИЕ РЕБЕНКА из СТУДИИ
@app.route('/delete_child/<int:child_id>', methods=['GET', 'POST'])
def delete_child(child_id):

    # delete_in_spisok(child_id)
    delete_in_spisok_in_studya(child_id)
    children = get_children(session['username'])

    return render_template('spisok.html', children=children, show_load_button=False)


## ------------- Работа со справочником конкурсов  --------- ##

## КОНКУРСЫ
@app.route('/events')
def events():
    events_t = get_events()

    return render_template('events.html', events=events_t, levels=levels)


## ДОБАВЛЕНИЕ КОНКУРСА
@app.route('/add_konkurs', methods=['GET', 'POST'])
def add_konkurs():
    event_types = get_event_types()
    if request.method == 'POST':
        result = add_in_event(request)
        return redirect(url_for('events'))
    return render_template('add_event.html', levels=levels, event_types=event_types)

## РЕДАКТИРОВАНИЕ конкурса
@app.route('/edit_event_inevent/<int:id_event>', methods=['GET', 'POST'])
def edit_event_inevent(id_event):
    ev = get_events_by_id(id_event)
    event_types = get_event_types()
    if request.method == 'POST':
        edit_in_events(request, id_event)
        return redirect(url_for('events'))
    else:
        return render_template('edit_event_in_event.html', event=ev, levels=levels, event_types=event_types)


## УДАЛЕНИЕ КОНКУРСА
@app.route('/delete_event/<int:id_event>', methods=['GET', 'POST'])
def delete_event(id_event):
    del_event(id_event)
    return redirect(url_for('events'))

## Отчет
@app.route('/otchet/<int:period>', methods=['GET'])
def otchet(period):
    user = session.get('username')

    if not user:
        flash('Пользователь не авторизован.', 'error')
        return redirect(request.referrer or '/')

    year_1 = session.get('year_1')
    year_2 = session.get('year_2')
    file_path = files.update_excel_template(user, period, year_1, year_2)

    file_name ='output.xlsx'
    return send_file(file_path, as_attachment=True, download_name=file_name)


@app.route('/report_form')
def report_form():
    if session.get('username') != 'admin':
        flash("Доступ запрещён", "error")
        return redirect(url_for('index'))

    year_1, year_2 = get_user_year_settings(session.get('username'))

    # Получаем все доступные варианты фильтрации
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM spr_studya")
    studios = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT id, name FROM spr_napravlenie")
    directions = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT id, FIO FROM teacher")
    teachers = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT id, name FROM event_type")
    event_types = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT year_1, year_2 FROM user_settings")
    years = [f"{row['year_1']}–{row['year_2']}" for row in cursor.fetchall()]

    conn.close()

    return render_template(
        'report_form.html',
        studios=studios,
        directions=directions,
        teachers=teachers,
        event_types=event_types,
        year = years,
        year1=year_1,
        year2=year_2,
    )

@app.route('/generate_report', methods=['POST'])
def generate_report():
    if session.get('username') != 'admin':
        flash("Доступ запрещён", "error")
        return redirect(url_for('index'))

    # Получаем параметры из формы
    date_start = request.form.get('date_start', '').strip()
    date_end = request.form.get('date_end', '').strip()

    studio_id = request.form.get('studio', '').strip()
    direction_id = request.form.get('direction', '').strip()
    teacher_id = request.form.get('teacher', '').strip()
    event_type_id = request.form.get('event_type', '').strip()

    # Проверяем даты (если указаны)
    if date_start and date_end and date_start > date_end:
        flash("Ошибка: Дата 'По' не может быть раньше даты 'С'", "error")
        return redirect(request.referrer or url_for('report_form'))

    # Сохраняем фильтры в сессии, чтобы передать их в /view_report
    session['report_filters'] = {
        'date_start': date_start,
        'date_end': date_end,
        'studio': studio_id,
        'direction': direction_id,
        'teacher': teacher_id,
        'event_type': event_type_id
    }

    # Редиректим на страницу просмотра данных
    return redirect(url_for('view_report'))


@app.route('/view_report')
def view_report():
    if session.get('username') != 'admin':
        flash("Доступ запрещён", "error")
        return redirect(url_for('index'))

    # Получаем фильтры из сессии
    filters = session.get('report_filters', {})
    if not filters:
        flash("Нет данных для отчета", "error")
        return redirect(url_for('report_form'))

    # Подключаемся к базе
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Получаем данные по фильтрам
    query = """
        SELECT 
            s.fio AS 'Обучающийся',
            s.date_bd AS 'Дата рождения',
            n.name AS 'Направление',
            st.name AS 'Студия',
            t.FIO AS 'Педагог',
            e.name AS 'Конкурс',
            e.level AS 'Уровень конкурса',
            et.name AS 'Тип конкурса',
            dt.result AS 'Результат',
            dt.date_otcheta AS 'Дата отчета',
            dt.file AS 'Файл'
        FROM data_table dt
        JOIN spisok s ON dt.id_spisok = s.id
        JOIN spisok_in_studio si ON dt.id_spisok_in_studio = si.id
        JOIN spr_studya st ON si.studio = st.id
        JOIN spr_napravlenie n ON si.napravlenie = n.id
        JOIN teacher t ON si.pedagog = t.id
        JOIN events_table e ON dt.id_events_table = e.id
        LEFT JOIN event_type et ON e.type_event_id = et.id
        WHERE 1=1
    """

    params = []

    # Фильтрация по датам
    if filters.get('date_start') and filters.get('date_end'):
        query += " AND dt.date_otcheta BETWEEN ? AND ?"
        params.extend([filters['date_start'], filters['date_end']])
    elif filters.get('date_start'):
        query += " AND dt.date_otcheta >= ?"
        params.append(filters['date_start'])
    elif filters.get('date_end'):
        query += " AND dt.date_otcheta <= ?"
        params.append(filters['date_end'])

    # Остальные фильтры
    if filters.get('studio'):
        query += " AND st.id = ?"
        params.append(filters['studio'])

    if filters.get('direction'):
        query += " AND n.id = ?"
        params.append(filters['direction'])

    if filters.get('teacher'):
        query += " AND t.id = ?"
        params.append(filters['teacher'])

    if filters.get('event_type'):
        query += " AND et.id = ?"
        params.append(filters['event_type'])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Преобразуем данные в список словарей
    columns = [description[0] for description in cursor.description]
    data = [dict_from_row(row) for row in rows]
    session['report_data'] = data

    # Передаем данные в шаблон
    return render_template(
        'universal_table.html',
        columns=columns,
        data=data,
        studios=get_all_studios(),     # функция получения студий
        directions=get_all_directions(),
        teachers=get_all_teachers(),
        event_types=get_all_event_types()
    )


@app.route('/export_to_excel')
def export_to_excel():
    if session.get('username') != 'admin':
        flash("Доступ запрещён", "error")
        return redirect(url_for('index'))

    data = session.get('report_data', [])
    if not data:
        flash("Нет данных для экспорта", "error")
        return redirect(url_for('view_report'))

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Отчет')

    output.seek(0)
    filename = f'report_{datetime.now().strftime("%Y%m%d")}.xlsx'

    return send_file(
        output,
        download_name=filename,
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/download_files_from_report')
def download_files_from_report():
    if session.get('username') != 'admin':
        flash("Доступ запрещён", "error")
        return redirect(url_for('index'))

    data = session.get('report_data', [])
    if not data:
        flash("Нет файлов для скачивания", "error")
        return redirect(url_for('view_report'))

    files = [row['Файл'] for row in data if row.get('Файл')]

    if not files:
        flash("Нет прикрепленных файлов", "info")
        return redirect(url_for('view_report'))

    # Для нескольких файлов — создаём ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                zip_file.write(file_path, filename)

    zip_buffer.seek(0)
    zip_filename = f'report_files_{datetime.now().strftime("%Y%m%d")}.zip'

    return send_file(
        zip_buffer,
        download_name=zip_filename,
        as_attachment=True,
        mimetype='application/zip'
    )


## ------------- Базовые справочники  --------- ##
@app.route('/reference/<ref_type>')
def reference(ref_type):
    # Поддерживаемые справочники
    tables = {
        'event_type': 'event_type',
        'napravlenie': 'spr_napravlenie',
        'studya': 'spr_studya',
        'teacher': 'teacher'
    }

    if ref_type not in tables:
        flash("Неизвестный справочник", "error")
        return redirect(url_for('index'))

    table_name = tables[ref_type]
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    titles = {
        'event_type': 'Типы конкурсов',
        'napravlenie': 'Направления',
        'studya': 'Студии',
        'teacher': 'Педагоги'
    }

    return render_template('reference.html', items=items, title=titles[ref_type], ref_type=ref_type)


@app.route('/reference/<ref_type>/add', methods=['POST'])
def add_reference(ref_type):
    tables = {
        'event_type': 'event_type',
        'napravlenie': 'spr_napravlenie',
        'studya': 'spr_studya',
        'teacher': 'teacher'
    }

    if ref_type not in tables:
        flash("Неизвестный справочник", "error")
        return redirect(url_for('index'))

    table_name = tables[ref_type]
    name = request.form.get('name')

    if not name:
        flash("Введите название", "error")
        return redirect(url_for('reference', ref_type=ref_type))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table_name} (name) VALUES (?)", (name,))
        conn.commit()
    except Exception as e:
        flash(f"Ошибка: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for('reference', ref_type=ref_type))


@app.route('/reference/<ref_type>/edit/<int:id>', methods=['GET', 'POST'])
def edit_reference(ref_type, id):
    tables = {
        'event_type': 'event_type',
        'napravlenie': 'spr_napravlenie',
        'studya': 'spr_studya',
        'teacher': 'teacher'
    }

    if ref_type not in tables:
        flash("Неизвестный справочник", "error")
        return redirect(url_for('index'))

    table_name = tables[ref_type]

    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            conn = get_db_connection()
            conn.execute(f"UPDATE {table_name} SET name = ? WHERE id = ?", (name, id))
            conn.commit()
            conn.close()
        return redirect(url_for('reference', ref_type=ref_type))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (id,))
    item = dict(cursor.fetchone())
    conn.close()

    return render_template('edit_reference.html', item=item, ref_type=ref_type)


@app.route('/reference/<ref_type>/delete/<int:id>')
def delete_reference(ref_type, id):
    tables = {
        'event_type': 'event_type',
        'napravlenie': 'spr_napravlenie',
        'studya': 'spr_studya',
        'teacher': 'teacher'
    }

    if ref_type not in tables:
        flash("Неизвестный справочник", "error")
        return redirect(url_for('index'))

    table_name = tables[ref_type]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (id,))
        conn.commit()
        flash("Запись удалена", "success")
    except Exception as e:
        flash(f"Ошибка удаления: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for('reference', ref_type=ref_type))

#-------------------  TEACHERS -------------------
@app.route('/teachers')
def teachers():
    if session.get('username') != 'admin':
        flash("Доступ запрещён", "error")
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teacher")
    teachers_list = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template('teachers.html', teachers=teachers_list)


@app.route('/teacher/add', methods=['POST'])
def add_teacher():
    if session.get('username') != 'admin':
        flash("Нет прав для добавления", "error")
        return redirect(url_for('index'))

    fio = request.form.get('fio')
    password = request.form.get('password')

    if not fio or not password:
        flash("Все поля обязательны", "error")
        return redirect(url_for('teachers'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO teacher (FIO, password) VALUES (?, ?)", (fio, password))
        conn.commit()
        flash("Педагог добавлен", "success")
    except sqlite3.IntegrityError:
        flash("Педагог с таким ФИО уже существует", "error")
    finally:
        conn.close()

    return redirect(url_for('teachers'))


@app.route('/teacher/<int:teacher_id>/edit', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    if session.get('username') != 'admin':
        flash("Доступ запрещён", "error")
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        new_fio = request.form.get('fio')
        new_password = request.form.get('password')
        if new_fio and new_password:
            cursor.execute("UPDATE teacher SET FIO = ?, password = ? WHERE id = ?", (new_fio, new_password, teacher_id))
            conn.commit()
            flash("Данные обновлены", "success")
        else:
            flash("Заполните все поля", "error")
        conn.close()
        return redirect(url_for('teachers'))

    cursor.execute("SELECT * FROM teacher WHERE id = ?", (teacher_id,))
    teacher = dict(cursor.fetchone())
    conn.close()

    return render_template('edit_teacher.html', teacher=teacher)


@app.route('/teacher/<int:teacher_id>/delete')
def delete_teacher(teacher_id):
    if session.get('username') != 'admin':
        flash("Доступ запрещён", "error")
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teacher WHERE id = ?", (teacher_id,))
        conn.commit()
        flash("Педагог удален", "success")
    except Exception as e:
        flash(f"Ошибка: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for('teachers'))




@app.route('/set_year', methods=['POST'])
def set_year():
    try:
        year_1 = int(request.form.get('year_1'))
        year_2 = int(request.form.get('year_2'))

        if year_2 != year_1 + 1:
            flash("Годы должны быть последовательными!", "error")
        else:
            session['year_1'] = year_1
            session['year_2'] = year_2
            set_user_year_settings(session['username'], year_1, year_2)
            flash(f"Учебный год изменен: {year_1}–{year_2}", "success")
    except:
        flash("Некорректные значения годов.", "error")

    return redirect(url_for('index'))


@app.route('/set_year_form')
def set_year_form():
    return render_template('set_year.html')


@app.route('/delete_file', methods=['POST'])
def delete_file():
    record_id = request.form.get('record_id')
    if not record_id:
        return jsonify({'success': False, 'message': 'Не указан ID записи'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Получаем текущую запись
        cursor.execute("SELECT file FROM data_table WHERE id = ?", (record_id,))
        record = cursor.fetchone()
        if not record:
            return jsonify({'success': False, 'message': 'Запись не найдена'})

        old_file_name = record['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_file_name)

        # Удаляем файл с диска
        if old_file_name and os.path.exists(file_path):
            os.remove(file_path)

        # Очищаем поля в БД
        cursor.execute("""
            UPDATE data_table 
            SET file = NULL, original_name = NULL 
            WHERE id = ?
        """, (record_id,))

        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

UPLOAD_FOLDER = 'static/load/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
