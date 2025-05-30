
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask import session
import json
import pandas as pd


import load_data, files
import os
# from SQL import *
from sql_utils import *

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
@app.route('/spisok_in_event/<int:event>')
def spisok_in_event(event):
    print('f')
    if session['username'] == 'admin':
        show_load_button = True
    else:
        show_load_button = False
    children = get_child_by_spisok_1(session['username'], event)  # Получаем список детей из базы данных
    return render_template('spisok_event.html', children=children, show_load_button=show_load_button)


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
        data = get_data_by_id_spisok(child[0], user=session['username'])
        events = get_events()
        return render_template('child_profile.html', events = events, child=child, data=data, docs=docs)
    return "Ребенок не найден", 404


## --------------- Работа с маршрутом --------------------##

# Настройте папку для загрузки файлов
UPLOAD_FOLDER = 'load'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Добавление записи об участии в мероприятии
@app.route('/add_data_entry/<int:child_id>', methods=['GET', 'POST'])
def add_data_entry(child_id):
    # child = get_child_by_id(child_id)  # Получаем информацию о ребенке по ID
    child = get_child_in_studya_by_id(child_id)

    if request.method == 'GET':
        # Получите данные детей и конкурсов из БД
        children = get_children(session['username'])  # Ваша функция для получения детей

        events = get_events()  # Ваша функция для получения конкурсов
        return render_template('edit_field.html', child = child, children=children, events=events, docs=docs, id_child=child_id)
       # Обработка POST запроса здесь
    elif request.method == 'POST':
        # id_spisok = request.form['id_spisok']
        save_in_date_table(request)
        return redirect(url_for('child_profile', child_id = child_id))


#загрузка файла
@app.route('/upload_file', methods=['POST'])
def upload_file():
    # Обработка загрузки файла
    file_name = request.form.get('saved_file_name')

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

# запись в базу об участии в конкурсе
@app.route('/save_data', methods=['POST'])
def save_data():

    id_spisok = request.form.get('id_spisok')

    if request.method =='POST':
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
    print(children)
    return render_template('spisok.html', children=children, show_load_button=False)


## ------------- Работа со справочником конкурсов  --------- ##

## КОНКУРСЫ
@app.route('/events')
def events():
    events_t = get_events()
    print('1')
    return render_template('events.html', events=events_t, levels=levels)


## ДОБАВЛЕНИЕ КОНКУРСА
@app.route('/add_konkurs', methods=['GET', 'POST'])
def add_konkurs():
    if request.method == 'POST':
        result = add_in_event(request)
        # return result
        return redirect(url_for('events'))
    return render_template('add_event.html', levels=levels)

## РЕДАКТИРОВАНИЕ конкурса
@app.route('/edit_event_inevent/<int:id_event>', methods=['GET', 'POST'])
def edit_event_inevent(id_event):
    ev = get_events_by_id(id_event)

    if request.method == 'POST':
        edit_in_events(request, id_event)
        return redirect(url_for('events'))
    else:
        return render_template('edit_event_in_event.html', event=ev, levels=levels)  #


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
            'id': child.get('id'),
            'fio': child.get('fio'),
            'studio': child.get('studio_name'),
            'teacher': child.get('teacher_name')
        })

    return jsonify(result)


@app.route('/event/<int:event_id>/add', methods=['POST'])
def add_to_event(event_id):
    if request.method != 'POST':
        return jsonify({'success': False, 'message': 'Метод не поддерживается'}), 405

    try:
        data = request.get_json()
        children_ids = data.get('children', [])

        if not children_ids:
            return jsonify({'success': False, 'message': 'Не выбран ни один участник'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли конкурс
        cursor.execute("SELECT 1 FROM events_table WHERE id = ?", (event_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Конкурс не найден'}), 404

        added_count = 0
        for child_id in children_ids:
            # Проверяем, существует ли ребенок
            cursor.execute("SELECT 1 FROM spisok WHERE id = ?", (child_id,))
            if not cursor.fetchone():
                continue  # Пропускаем несуществующих детей

            # Проверяем, не участвует ли уже ребенок в этом конкурсе
            cursor.execute("""
                SELECT 1 FROM data_table 
                WHERE id_events_table = ? AND id_spisok = ?
            """, (event_id, child_id))

            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO data_table (id_events_table, id_spisok)
                    VALUES (?, ?)
                """, (event_id, child_id))
                added_count += 1

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'added': added_count,
            'message': f'Успешно добавлено {added_count} участников'
        })

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Ошибка при добавлении: {str(e)}'}), 500

UPLOAD_FOLDER = 'static/load/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
