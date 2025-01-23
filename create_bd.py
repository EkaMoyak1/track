import sqlite3
import SQL

def create_tables():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()

    # Создаем новую таблицу spisok - весь список детей
    sql_create_spisok = '''
    CREATE TABLE IF NOT EXISTS spisok (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fio TEXT NOT NULL,
        date_bd DATE NOT NULL,
        age INT
    );
    '''
    cursor_db.execute(sql_create_spisok)
    db_lp.commit()

    # Создаем новую таблицу spisok_in_studio - дети в студиях
    sql_create_spisok_in_studio = '''
    CREATE TABLE IF NOT EXISTS spisok_in_studio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_spisok INTEGER NOT NULL,
        napravlenie INTEGER NOT NULL,
        studio INTEGER NOT NULL,
        pedagog INTEGER NOT NULL,
        FOREIGN KEY (id_spisok) REFERENCES spisok(id)
    );
    '''
    cursor_db.execute(sql_create_spisok_in_studio)
    db_lp.commit()

    # Справочник конкурсов
    sql_create = '''CREATE TABLE if NOT exists events_table(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    opisanie TEXT,
                    srok_podachi_date DATE,
                    result_date DATE
                    );'''

    cursor_db.execute(sql_create)
    db_lp.commit()

    # Участие детей в конкурсах
    sql_create = '''CREATE TABLE if NOT exists data_table(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_spisok int NOT NULL,
                    id_spisok_in_studio INTEGER NOT NULL,
                    id_events_table int NOT NULL,
                    result TEXT,
                    original_name TEXT,
                    file TEXT,
                    date_otcheta DATE
                    );'''

    cursor_db.execute(sql_create)
    db_lp.commit()


    sql_create = '''CREATE TABLE if NOT exists spr_napravlenie(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                     );'''

    cursor_db.execute(sql_create)
    db_lp.commit()

    sql_create = '''CREATE TABLE if NOT exists spr_studya(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                     );'''

    cursor_db.execute(sql_create)
    db_lp.commit()

    sql_create = '''CREATE TABLE if NOT exists studyas_in_napravlenie(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_studya int NOT NULL,
                    id_napravlenie int NOT NULL
                     );'''

    cursor_db.execute(sql_create)
    db_lp.commit()

    sql_create = '''CREATE TABLE if NOT exists teacher(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    FIO TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                     );'''

    cursor_db.execute(sql_create)
    db_lp.commit()

    cursor_db.close()
    db_lp.close()



def show_tbl(table):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute('SELECT * from '+table)

    # Сохранение изменений в базе данных
    db_lp.commit()
    tbl = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    print(tbl)

def drop_table(name):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    # Удаление всех записей из таблицы data_table
    sql_delete_all = 'DELETE FROM data_table;'
    cursor_db.execute(sql_delete_all)

    # Подтверждение изменений
    db_lp.commit()

    # Закрытие соединения с базой данных
    db_lp.close()


import pandas as pd


def add_column_to_table(table_name, column_name, column_type):
    db_lp = sqlite3.connect('date_source.db')
    cursor = db_lp.cursor()

    # Создаем SQL-запрос для добавления нового столбца
    sql_add_column = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"

    try:
        # Выполняем SQL-запрос
        cursor.execute(sql_add_column)

        # Фиксируем изменения в базе данных
        db_lp.commit()



        print(f"Столбец '{column_name}' добавлен в таблицу '{table_name}'.")
    except Exception as e:
        # Обработка возможных ошибок
        print(f"Ошибка при добавлении столбца '{column_name}': {e}")

    # Закрытие соединения с базой данных
    db_lp.close()

def test():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()

    # Выполнение запроса
    cursor_db.execute('''
                      SELECT
                            teacher.FIO AS teacher_name,
                            spisok.fio AS student_name,
                            events_table.name AS event_name,
                            strftime('%m', events_table.result_date) AS result_month, 
                            data_table.result AS event_result
                        FROM
                            data_table
                        JOIN spisok ON data_table.id_spisok = spisok.id
                        JOIN spisok_in_studio ON data_table.id_spisok_in_studio = spisok_in_studio.id
                        JOIN teacher ON spisok_in_studio.pedagog = teacher.id
                        JOIN events_table ON data_table.id_events_table = events_table.id
                        ORDER BY teacher_name, event_name, student_name;
                       ''')

    # Извлечение данных
    data = cursor_db.fetchall()
    columns = [description[0] for description in cursor_db.description]

    # Закрытие соединения с базой данных
    cursor_db.close()
    db_lp.close()

    # Создание DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Сохранение в Excel
    df.to_excel('output.xlsx', index=False)

    print("Данные успешно сохранены в файл output.xlsx")

if __name__ == '__main__':
    # create_tables()1
    # SQL.add_super_user()
    # show_tbl('teacher')
    print('1 - show')
    print('2 - drop')
    print('3 - test')

    rej = int(input('выберите режим '))

    if rej == 3:
        # test()
        add_column_to_table("data_table", "date_otcheta", "DATE")
    else:

        print()
        print('1 - spisok - дети')
        print('2 - spisok_in_studio - дети в студиях')
        print('3 - events_table')
        print('4 - data_table')
        print('5 - spr_napravlenie')
        print('6 - spr_studya')
        print('7 - studyas_in_napravlenie')
        print('8 - teacher')
        tab = int(input('выберите таблицу '))
        name=''
        if tab == 1:
            name = 'spisok'
        elif tab == 2:
            name = 'spisok_in_studio'
        elif tab == 3:
            name = 'events_table'
        elif tab == 4:
            name = 'data_table'
        elif tab == 5:
            name = 'spr_napravlenie'
        elif tab == 6:
            name = 'spr_studya'
        elif tab == 7:
            name = 'studyas_in_napravlenie'
        elif tab == 8:
            name = 'teacher'

        if rej==1:
            show_tbl(name)
        elif rej==2:
            r = input(' Вы уверены очистить все данные? (Y/N) ')
            if r == 'Y':
                drop_table(name)



