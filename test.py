import pandas as pd
import sqlite3
import os
from datetime import datetime


def calculate_age(birth_date):
    # Получаем текущую дату
    today = datetime.today()
    # Вычисляем возраст в полных годах
    age = today.year - birth_date.year
    # Учитываем, прошел ли день рождения в текущем году
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def update_teacher(excel_file_path):
    # Чтение данных со третьего листа (Педагоги)
    teacher_table_df = pd.read_excel(excel_file_path, sheet_name=2)

    # Загрузка данных в таблицу teacher построчно
    for index, row in teacher_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        print(row_data)


def update_studyas(excel_file_path):
    # Чтение данных со 4 листа (Студии)
    spr_studya_table_df = pd.read_excel(excel_file_path, sheet_name=3)

    # Загрузка данных в таблицу spr_studya построчно
    for index, row in spr_studya_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        print(row_data)




def update_spisok(excel_file_path):
    # Чтение данных с 5 листа (spisok)
    spisok_df = pd.read_excel(excel_file_path, sheet_name=4)

    # Загрузка данных в таблицу spisok построчно
    for index, row in spisok_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        result_date = row_data[1]
        result_date_data = result_date.strftime('%Y-%m-%d')
        age = calculate_age(result_date)



def update_spisok_in_stud(excel_file_path, db_lp, cursor_db):
    # Чтение данных с первого листа (spisok)
    spisok_df = pd.read_excel(excel_file_path, sheet_name=0)

    # Загрузка данных в таблицу spisok_in_studio построчно

    for index, row in spisok_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        fio = row_data[0]
        cursor_db.execute('SELECT * FROM spisok  WHERE fio = ?', (fio,))
        data = cursor_db.fetchall()
        id_spisok = 0
        for d in data:
            id_spisok = d[0]
            break
        if len(data) > 1:
            print('fio=', fio, 'дубль')
        elif len(data) == 0:
            print('fio не обнаружен')
        # print(row_data)

        if row_data[3].lower() == 'техническое':
            napravlenie = 1
        elif row_data[3].lower() == 'художественное':
            napravlenie = 2
        else:
            napravlenie = 3

        cursor_db.execute('SELECT * FROM spr_studya')
        data = cursor_db.fetchall()
        studio = '0'
        for d in data:
            if d[1] == str(row_data[4]):
                studio = d[0]
                break

        cursor_db.execute('SELECT * FROM teacher')
        data = cursor_db.fetchall()
        # print(data)
        teacher = '0'
        for d in data:
            print(row_data[5])
            if d[1].strip() == str(row_data[5]).strip():
                teacher = d[0]
                break

        print(id_spisok, napravlenie, studio, teacher)




def update_events(excel_file_path):
    # Чтение данных со второго листа (events_table)
    events_table_df = pd.read_excel(excel_file_path, sheet_name=6)

    # Загрузка данных в таблицу events_table построчно
    for index, row in events_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        print(row_data)

        srok_podachi_date = row_data[2].strftime('%Y-%m-%d') if isinstance(row_data[2], pd.Timestamp) else row_data[2]
        result_date = row_data[3].strftime('%Y-%m-%d') if isinstance(row_data[3], pd.Timestamp) else row_data[3]
        print(srok_podachi_date, result_date)


def load_data():

    # Подключение к базе данных
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()

    # Загрузка данных из Excel-файла
    excel_file_path = 'data.xlsx'  # Укажите путь к вашему Excel-файлу
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Файл {excel_file_path} не найден.")

    update_teacher(excel_file_path)

    update_studyas(excel_file_path)

    update_spisok(excel_file_path)

    update_spisok_in_stud(excel_file_path, db_lp, cursor_db)

    update_events(excel_file_path, db_lp, cursor_db)

    # Закрытие соединения с базой данных
    cursor_db.close()
    db_lp.close()


excel_file_path1 = 'data-ver-2.xlsx'  # Укажите путь к вашему Excel-файлу
if not os.path.exists(excel_file_path1):
    raise FileNotFoundError(f"Файл {excel_file_path1} не найден.")

update_events(excel_file_path1)
