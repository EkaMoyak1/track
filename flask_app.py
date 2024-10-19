from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import sqlite3
import load_data
import os
from SQL import *
import uuid

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
    return render_template('spisok.html', children=children, show_load_button = False)

@app.route('/karta')
def karta():
    children = (get_children())  # Получаем список детей из базы данных
    table_res = []
    for child in children:
        ev = get_data_by_id_spisok_kor(child[0])
        table_res.append([child[1],list(ev), child[0]])

    return render_template('children_profiles.html', children=table_res)

@app.route('/events')
def events():
    events_t = get_events()
    return render_template('events.html', events=events_t)

@app.route('/child/<int:child_id>')
def child_profile(child_id):
    child = get_child_by_id(child_id)
    if child:
        data = get_data_by_id_spisok(child_id)
        events = get_events()
        return render_template('child_profile.html', events = events, child=child, data=data, docs=docs)
    return "Ребенок не найден", 404



# Настройте папку для загрузки файлов
UPLOAD_FOLDER = 'load'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/add_data_entry', methods=['GET', 'POST'])

#Добавление записи об участии в мероприятии
def add_data_entry():
    child_id = request.args.get('child_id')  # Получаем ID ребенка из URL
    child = get_child_by_id(child_id)  # Получаем информацию о ребенке по ID

    if request.method == 'GET':
        # Получите данные детей и конкурсов из БД
        children = get_children()  # Ваша функция для получения детей
        events = get_events()  # Ваша функция для получения конкурсов
        return render_template('edit_field.html', child = child, children=children, events=events, docs=docs, id_child=child_id)
       # Обработка POST запроса здесь
    elif request.method == 'POST':
        id_spisok = request.form['id_spisok']
        save_in_date_table(request)
        return redirect(url_for('child_profile', child_id = id_spisok))


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


@app.route('/add_child', methods=['GET', 'POST'])
def add_child():
    if request.method == 'POST':
        add_in_spisok(request)

        children = get_children()  # Получаем список детей из базы данных
        # return render_template('spisok.html', children=children, show_load_button=False)
        return redirect(url_for('spisok'))
    napr_table = get_napr()
    spr_studya = get_siudio()
    teacher = get_teacher()
    return render_template('add_child.html', napr_table=napr_table, spr_studya=spr_studya, teacher=teacher)  # Создайте этот шаблон


@app.route('/edit_child/<int:child_id>', methods=['GET', 'POST'])
def edit_child(child_id):
    child = get_child_by_id(child_id)
    if request.method == 'POST':
        # fio = request.form['fio']
        edit_in_spisok(request, child_id)
        children = get_children()  # Получаем список детей из базы данных
        # return render_template('spisok.html', children=children, show_load_button=False)
        return redirect(url_for('spisok'))

    else:
        napr_table = get_napr()
        spr_studya = get_siudio()
        teacher = get_teacher()
        return render_template('edit_child.html', child=child, napr_table=napr_table, spr_studya=spr_studya, teacher=teacher)  #



@app.route('/delete_child/<int:child_id>', methods=['GET', 'POST'])
def delete_child(child_id):

    delete_in_spisok(child_id)
    children = get_children()
    return render_template('spisok.html', children=children, show_load_button=False)


UPLOAD_FOLDER = 'static/load/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER






if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))