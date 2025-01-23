import pandas as pd
import sqlite3
import os
import create_bd
import SQL
from datetime import datetime
import numpy as np
from tkinter import filedialog, Tk


def calculate_age(birth_date):
    # Получаем текущую дату
    today = datetime.today()
    # Вычисляем возраст в полных годах
    age = today.year - birth_date.year
    # Учитываем, прошел ли день рождения в текущем году
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def clear_tables(cursor_db, db_lp):
    cursor_db.execute('DELETE FROM spisok')
    cursor_db.execute('DELETE FROM spisok_in_studio')
    cursor_db.execute('DELETE FROM events_table')
    cursor_db.execute('DELETE FROM data_table')  # Если необходимо очистить и эту таблицу
    cursor_db.execute('DELETE FROM spr_napravlenie')
    cursor_db.execute('DELETE FROM spr_studya')
    cursor_db.execute('DELETE FROM teacher')
    cursor_db.execute('DELETE FROM studyas_in_napravlenie')
    db_lp.commit()


def sbros_id(cursor_db, db_lp):
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="spisok"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="spisok_in_studio"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="events_table"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="data_table"')  # Если необходимо
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="spr_napravlenie"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="spr_studya"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="teacher"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="studyas_in_napravlenie"')
    db_lp.commit()


def update_napr(cursor_db, db_lp):
    cursor_db.execute('''
                    INSERT INTO spr_napravlenie (name)
                    VALUES (?)
                ''', ('Техническое',))
    cursor_db.execute('''
                    INSERT INTO spr_napravlenie (name)
                    VALUES (?)
                ''', ('Художественное',))
    cursor_db.execute('''
                    INSERT INTO spr_napravlenie (name)
                    VALUES (?)
                ''', ('Социально-гуманитарное',))

    # Сохранение изменений в базе данных
    db_lp.commit()


def update_teacher(excel_file_path, db_lp, cursor_db):
    # Чтение данных со третьего листа (Педагоги)
    teacher_table_df = pd.read_excel(excel_file_path, sheet_name=2)

    # Загрузка данных в таблицу teacher построчно
    for index, row in teacher_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()

        # Вставка данных в таблицу teacher
        cursor_db.execute('''
                    INSERT INTO teacher (FIO, password)
                    VALUES (?, ?)
                ''', (row_data[0], 'cdo2024'))

    # Сохранение изменений в базе данных
    db_lp.commit()


def update_studyas(excel_file_path, db_lp, cursor_db):
    # Чтение данных со 4 листа (Студии)
    spr_studya_table_df = pd.read_excel(excel_file_path, sheet_name=3)

    # Загрузка данных в таблицу spr_studya построчно
    for index, row in spr_studya_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        print(row_data)

        # Вставка данных в таблицу spr_studya
        cursor_db.execute('''
                       INSERT INTO spr_studya (name)
                       VALUES (?)
                   ''', row_data)

    # Сохранение изменений в базе данных
    db_lp.commit()


def update_spisok(excel_file_path, db_lp, cursor_db):
    # Чтение данных с 5 листа (spisok)
    spisok_df = pd.read_excel(excel_file_path, sheet_name=4)

    # Загрузка данных в таблицу spisok построчно
    for index, row in spisok_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        result_date = row_data[1]
        result_date_data = result_date.strftime('%Y-%m-%d')
        age = calculate_age(result_date)
        if row_data[3] != 2:
            print(row_data[0], row_data[3])
            cursor_db.execute('''
                    INSERT INTO spisok (fio, date_bd, age)
                    VALUES (?, ?, ?)
                ''', (row_data[0], result_date_data, age))

    # Сохранение изменений в базе данных
    db_lp.commit()


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
        teacher = '0'
        for d in data:
            if d[1].strip() == str(row_data[5]).strip():
                teacher = d[0]
                break

        cursor_db.execute('''
                INSERT INTO spisok_in_studio (id_spisok, napravlenie, studio, pedagog)
                VALUES (?, ?, ?, ?)
            ''', (id_spisok, napravlenie, studio, teacher))

    # Сохранение изменений в базе данных
    db_lp.commit()


def update_spisok_add(excel_file_path, db_lp, cursor_db):
    # Чтение данных с 5 листа (spisok)
    spisok_df = pd.read_excel(excel_file_path, sheet_name=4)

    # Загрузка данных в таблицу spisok построчно
    for index, row in spisok_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        result_date = row_data[1]
        result_date_data = result_date.strftime('%Y-%m-%d')
        age = calculate_age(result_date)
        if row_data[3] != 2:
            print(row_data[0], row_data[3])
            cursor_db.execute('''
                    INSERT INTO spisok (fio, date_bd, age)
                    VALUES (?, ?, ?)
                ''', (row_data[0], result_date_data, age))

    # Сохранение изменений в базе данных
    db_lp.commit()


def update_events(excel_file_path, db_lp, cursor_db):
    # Чтение данных со второго листа (events_table)
    events_table_df = pd.read_excel(excel_file_path, sheet_name=6)

    # Загрузка данных в таблицу events_table построчно
    for index, row in events_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        # Преобразование NaN и NaT в пустые строки

        srok_podachi_date = row_data[2].strftime('%Y-%m-%d') if isinstance(row_data[2], pd.Timestamp) else row_data[2]
        result_date = row_data[3].strftime('%Y-%m-%d') if isinstance(row_data[3], pd.Timestamp) else row_data[3]
        cleaned_data1, cleaned_data2 = ["" if isinstance(x, (float, pd._libs.tslibs.nattype.NaTType)) or pd.isna(x) else x for x in  [srok_podachi_date, result_date]]

        print(row_data[0], row_data[1], cleaned_data1, cleaned_data2)
        # Вставка данных в таблицу events_table
        cursor_db.execute('''
                INSERT INTO events_table (name, opisanie, srok_podachi_date, result_date)
                VALUES (?, ?, ?, ?)
            ''', (row_data[0], row_data[1], cleaned_data1, cleaned_data2))

    # Сохранение изменений в базе данных
    db_lp.commit()

def update_st_in_napr(excel_file_path, db_lp, cursor_db):
    # Чтение данных со 4 листа (events_table)

    events_table_df = pd.read_excel(excel_file_path, sheet_name=3)

def load_data():

    # Создание таблиц, если они не существуют
    create_bd.create_tables()

    # Подключение к базе данных
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()

    # Очистка данных в таблицах перед загрузкой новых данных
    clear_tables(cursor_db, db_lp)

    # Сброс автоинкремента для каждой таблицы
    sbros_id(cursor_db, db_lp)

    # справочник направлений
    update_napr(cursor_db, db_lp)

    # Загрузка данных из Excel-файла
    excel_file_path = 'data-ver-2.xlsx'  # Укажите путь к вашему Excel-файлу
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Файл {excel_file_path} не найден.")

    update_teacher(excel_file_path, db_lp, cursor_db)

    update_studyas(excel_file_path, db_lp, cursor_db)

    update_spisok(excel_file_path, db_lp, cursor_db)

    update_spisok_in_stud(excel_file_path, db_lp, cursor_db)

    update_events(excel_file_path, db_lp, cursor_db)

    SQL.add_super_user()

    # Закрытие соединения с базой данных
    cursor_db.close()
    db_lp.close()


def load_add(rej=0):
    pass
    # try:
    #     # Подключение к базе данных
    #     db_lp = sqlite3.connect('date_source.db')
    #     cursor_db = db_lp.cursor()
    #     if rej==0:
    #         cursor_db.execute('DELETE FROM spisok')
    #         cursor_db.execute('DELETE FROM spisok_in_studio')
    #         db_lp.commit()
    #
    # except:
    #     raise 'нет базы'
    # else:
    #     # Загрузка данных из Excel-файла
    #     excel_file_path = 'data-ver-3.xlsx'  # Укажите путь к вашему Excel-файлу
    #
    #     if not os.path.exists(excel_file_path):
    #         raise FileNotFoundError(f"Файл {excel_file_path} не найден.")
    #
    #     if rej==0:
    #         update_spisok_add(excel_file_path, db_lp, cursor_db)
    #
    #         update_spisok_in_stud(excel_file_path, db_lp, cursor_db)
    #     else:
    #         update_st_in_napr(excel_file_path, db_lp, cursor_db)
    #
    #
    #     # Закрытие соединения с базой данных
    #     cursor_db.close()
    #     db_lp.close()

def studio_in_napr():
    load_add(1)

if __name__ == '__main__':
    print('')
    # load_data()
    studio_in_napr()
