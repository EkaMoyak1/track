from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import sqlite3
import load_data
import os

app = Flask(__name__)

# Установите секретный ключ
app.secret_key = os.urandom(24)

docs =[' ', 'Сертификат участника',
        'Диплом 1 степени',
        'Диплом 2 степени',
        'Диплом 3 степени',
        'Лауреат',
        'Лауреат 1 степени',
        'Лауреат 2 степени',
        'Лауреат 3 cтепени']

# Функция для получения данных о конкретном ребенке по ID
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
    #cursor_db.execute("SELECT * FROM data_table  WHERE id_spisok = ?", (id_spisok,))
    cursor_db.execute('''
           SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                  events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date
           FROM data_table
           JOIN events_table ON data_table.id_events_table = events_table.id
           WHERE data_table.id_spisok = ?''', (id_spisok,))
    data = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return data

def  get_events():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM events_table")
    events_table = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    events_table = [[f.replace('"',"") if type(f)==str else f for f in s] for s in events_table]

    return events_table

def get_children():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM spisok")
    children = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return children

def get_data_by_id(record_id):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM data_table WHERE id = ?", (record_id,))
    record = cursor_db.fetchone()
    cursor_db.close()
    db_lp.close()
    return record

@app.route('/')
def index():
    children = get_children()
    return render_template('index.html', children=children)

@app.route('/load')
def load_data_route():
    load_data.load_data()  # Предполагается, что у вас есть функция load_data в load_data.py
    return redirect(url_for('index'))  # После завершения загрузки перенаправим на главную страницу

@app.route('/spisok')
def spisok():
    children = get_children()  # Получаем список детей из базы данных
    # print(children)
    return render_template('spisok.html', children=children)

@app.route('/events')
def events():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("SELECT * FROM events_table")
    events = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return render_template('events.html', events=events)

@app.route('/child/<int:child_id>')
def child_profile(child_id):
    child = get_child_by_id(child_id)
    if child:
        data = get_data_by_id_spisok(child_id)
        events = get_events()

        # if data:
        return render_template('child_profile.html', events = events, child=child, data=data, docs=docs)
        # else:
        #     return "Нет данных о конкурсах для данного ребенка", 404
        # return render_template('child_profile.html', child=child, data=data)
    return "Ребенок не найден", 404

@app.route('/add_data_entry', methods=['GET', 'POST'])
def add_data_entry():
    child_id = request.args.get('child_id')  # Получаем ID ребенка из URL
    child = get_child_by_id(child_id)  # Получаем информацию о ребенке по ID

    if request.method == 'GET':
        # Получите данные детей и конкурсов из БД
        children = get_children()  # Ваша функция для получения детей
        events = get_events()  # Ваша функция для получения конкурсов
        return render_template('edit_field.html', child = child, children=children, events=events, docs=docs, id_child=child_id)
       # Обработка POST запроса здесь
    else:
        try:

            id_spisok = request.form['id_spisok']
            id_events_table = request.form['id_events_table']
            doc_type = request.form['doc_type']
            print(id_spisok, id_events_table, doc_type)
            # Если необходимо обработать файл:
            # file = request.files['file']
            # if file:
            #     # Сохраните файл на сервере или обработайте его по вашему усмотрению
            #     file.save(f'uploads/{file.filename}')  # Пример сохранения файла

            # Сохранение данных в базе данных
            db_lp = sqlite3.connect('date_source.db')
            cursor_db = db_lp.cursor()
            cursor_db.execute("INSERT INTO data_table (id_spisok, id_events_table, result) VALUES (?, ?, ?)",
                              (id_spisok, id_events_table, doc_type))
            db_lp.commit()
            cursor_db.close()
            db_lp.close()
            print('Запись успешно добавлена')
            flash('Запись успешно добавлена', 'success')
        except KeyError as e:
            print('error')
            flash(f'Ошибка: отсутствует поле {e}', 'error')

    return child_profile(id_spisok)  # Перенаправление на главную страницу после добавления записи

@app.route('/edit_data_entry/<int:record_id>', methods=['GET', 'POST'])
def edit_data_entry(record_id):
    # Логика для редактирования записи
    data_entry = get_data_by_id(record_id)
    child = get_child_by_id(data_entry[1])
    if request.method == 'GET':
        # Получите данные детей и конкурсов из БД
        children = get_children()  # Ваша функция для получения детей
        events = get_events()  # Ваша функция для получения конкурсов
        return render_template('edit_data_entry.html', child=child, events=events, docs=docs,
                               data_entry=data_entry)

    else:
        try:
            # Обработка данных формы и обновление записи в базе данных
            # record_id = request.form['record_id']
            id_spisok = request.form['id_spisok']
            id_events_table = request.form['id_events_table']
            doc_type = request.form['doc_type']
            print(id_spisok, id_events_table, doc_type)

            # Обновление данных в базе данных
            db_lp = sqlite3.connect('date_source.db')
            cursor_db = db_lp.cursor()

            # Выполнение запроса на обновление
            cursor_db.execute("UPDATE data_table SET id_spisok = ?, id_events_table = ?, result = ? WHERE id = ?",
                              (id_spisok, id_events_table, doc_type, record_id))

            db_lp.commit()
            cursor_db.close()
            db_lp.close()

            print('Запись успешно изменена')
            flash('Запись успешно изменена', 'success')
        except KeyError as e:
            print('error')
            flash(f'Ошибка: отсутствует поле {e}', 'error')

    return child_profile(id_spisok)

@app.route('/delete_data_entry/<int:record_id>', methods=['POST'])
def delete_data_entry(record_id):
    # Логика удаления записи из базы данных
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute("DELETE FROM data_table WHERE id = ?", (record_id,))
    db_lp.commit()
    cursor_db.close()
    db_lp.close()


@app.route('/save_data', methods=['POST'])
def save_data():

    record_id = request.form.get('record-id')
    id_spisok =  request.form.get('id_spisok')
    id_events_table = request.form.get('id_events_table')
    result = request.form.get('id_doc_type')
    print('зап=',record_id, 'spis=', id_spisok, 'event=',id_events_table, result)

    try:
        # Подключение кбазе данных и вставка данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()

        cursor.execute('''UPDATE data_table
                          SET id_spisok = ?, id_events_table = ?, result = ?, file = ?
                          WHERE id = ?''', (id_spisok, id_events_table, result, " ", record_id))
        conn.commit()
        conn.close()
        print('Запись успешно изменена')
        flash('Запись успешно изменена', 'success')
    except KeyError as e:
        print('error')
        flash(f'Ошибка: отсутствует поле {e}', 'error')

    return child_profile(id_spisok)

@app.route('/delete_data', methods=['POST'])
def delete_data():
    record_id = request.form.get('record-id')
    # id_spisok = request.form.get('id_spisok')
    # print(id_spisok, record_id)
    try:
        # Подключение кбазе данных и вставка данных
        conn = sqlite3.connect('date_source.db')  # Укажите ваше имя базы данных
        cursor = conn.cursor()
        cursor.execute('SELECT id_spisok FROM data_table WHERE id = ?', (record_id,))
        child = cursor.fetchall()[0][0]
        print(child)
        cursor.execute('DELETE FROM data_table WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        print('Запись успешно удалена')
        flash('Запись успешно удалена', 'success')
    except KeyError as e:
        print('error')
        flash(f'Ошибка: отсутствует поле {e}', 'error')

    return child_profile(child)

if __name__ == '__main__':
    app.run(debug=True)