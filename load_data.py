import pandas as pd
import sqlite3
import os
import create_bd
import  SQL

def load_data():

    # Создание таблиц, если они не существуют
    create_bd.create_tables()

    # Подключение к базе данных
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()

    # Очистка данных в таблицах перед загрузкой новых данных
    cursor_db.execute('DELETE FROM spisok')
    cursor_db.execute('DELETE FROM events_table')
    cursor_db.execute('DELETE FROM data_table')  # Если необходимо очистить и эту таблицу
    cursor_db.execute('DELETE FROM spr_napravlenie')
    cursor_db.execute('DELETE FROM spr_studya')
    cursor_db.execute('DELETE FROM teacher')

    db_lp.commit()

    # Сброс автоинкремента для каждой таблицы
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="spisok"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="events_table"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="data_table"')  # Если необходимо
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="spr_napravlenie"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="spr_studya"')
    cursor_db.execute('DELETE FROM sqlite_sequence WHERE name="teacher"')
    db_lp.commit()


    #справочник направлений
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


    # Загрузка данных из Excel-файла
    excel_file_path = 'data.xlsx'  # Укажите путь к вашему Excel-файлу
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Файл {excel_file_path} не найден.")

    # Чтение данных со третьего листа (Педагоги)
    teacher_table_df = pd.read_excel(excel_file_path, sheet_name=2)

    # Загрузка данных в таблицу teacher построчно
    for index, row in teacher_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        print(row_data)

        # Вставка данных в таблицу events_table
        cursor_db.execute('''
                INSERT INTO teacher (FIO, password)
                VALUES (?, ?)
            ''', (row_data[0], 'cdo2024'))

    # Сохранение изменений в базе данных
    db_lp.commit()



    # Чтение данных со 4 листа (Студии)
    spr_studya_table_df = pd.read_excel(excel_file_path, sheet_name=3)

    # Загрузка данных в таблицу teacher построчно
    for index, row in spr_studya_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        print(row_data)

        # Вставка данных в таблицу events_table
        cursor_db.execute('''
                   INSERT INTO spr_studya (name)
                   VALUES (?)
               ''', row_data)

    # Сохранение изменений в базе данных
    db_lp.commit()




    # Чтение данных с первого листа (spisok)
    spisok_df = pd.read_excel(excel_file_path, sheet_name=0)

    # Загрузка данных в таблицу spisok построчно
    for index, row in spisok_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        result_date = row_data[1].strftime('%Y-%m-%d') if isinstance(row_data[1], pd.Timestamp) else row_data[1]
        # print(row_data)
        # Вставка данных в таблицу spisok

        if row_data[3].lower() == 'техническое':
            napravlenie = 1
        elif row_data[3].lower() == 'художественное':
            napravlenie = 2
        else:
            napravlenie = 3

        cursor_db.execute('SELECT * FROM spr_studya')
        data = cursor_db.fetchall()
        studio = '0'
        print(row_data)
        for d in data:
            if d[1] == str(row_data[4]):
                studio =d[0]
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

        cursor_db.execute('''
            INSERT INTO spisok (fio, date_bd, age, napravlenie, studio, pedagog)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row_data[0], result_date, row_data[2], napravlenie, studio, teacher))

    # Сохранение изменений в базе данных
    db_lp.commit()

    # Чтение данных со второго листа (events_table)
    events_table_df = pd.read_excel(excel_file_path, sheet_name=1)

    # Загрузка данных в таблицу events_table построчно
    for index, row in events_table_df.iterrows():
        # Преобразование строки в словарь
        row_data = row.tolist()
        print(row_data)

        srok_podachi_date = row_data[2].strftime('%Y-%m-%d') if isinstance(row_data[2], pd.Timestamp) else row_data[2]
        result_date = row_data[3].strftime('%Y-%m-%d') if isinstance(row_data[3], pd.Timestamp) else row_data[3]

        # Вставка данных в таблицу events_table
        cursor_db.execute('''
            INSERT INTO events_table (name, opisanie, srok_podachi_date, result_date)
            VALUES (?, ?, ?, ?)
        ''', (row_data[0],row_data[1], srok_podachi_date, result_date))

    # Сохранение изменений в базе данных
    db_lp.commit()

    SQL.add_super_user()

    # Закрытие соединения с базой данных
    cursor_db.close()
    db_lp.close()
