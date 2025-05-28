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
                    result_date DATE,
                    level TEXT
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

    sql_create = '''CREATE TABLE IF NOT EXISTS user_settings (
                    id TEXT PRIMARY KEY,
                    year_1 INTEGER DEFAULT 2024,
                    year_2 INTEGER DEFAULT 2025
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

    try:
        # Удаление всей таблицы
        cursor_db.execute(f"DROP TABLE IF EXISTS {name};")
        db_lp.commit()
        print(f"Таблица '{name}' успешно удалена.")
    except Exception as e:
        print(f"Ошибка при удалении таблицы '{name}': {e}")
    finally:
        db_lp.close()

def clear_table(name):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()

    try:
        cursor_db.execute(f"DELETE FROM {name};")
        db_lp.commit()
        print(f"Данные из таблицы '{name}' успешно удалены.")
    except Exception as e:
        print(f"Ошибка при очистке таблицы '{name}': {e}")
    finally:
        db_lp.close()


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
    sql_create = '''CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    year_1 INTEGER DEFAULT 2024,
                    year_2 INTEGER DEFAULT 2025
                     );'''

    cursor_db.execute(sql_create)
    db_lp.commit()

    cursor_db.close()
    db_lp.close()

if __name__ == '__main__':
    # create_tables()1
    # SQL.add_super_user()
    # show_tbl('teacher')
    print('1 - show')
    print('2 - drop')
    print('3 - test')

    rej = int(input('выберите режим '))

    if rej == 3:
       test()
        # add_column_to_table("events_table", "level", "TEXT")
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
        print('9 - user_settings')
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
        elif tab == 9:
            name = 'user_settings'

        if rej==1:
            show_tbl(name)
        elif rej==2:
            print("Выберите действие:")
            print("1 - Очистить данные в таблице (DELETE)")
            print("2 - Удалить таблицу полностью (DROP)")
            action = int(input("Введите номер действия: "))

            if action == 1:
                confirm = input("Вы уверены, что хотите очистить данные? (Y/N): ")
                if confirm == 'Y':
                    clear_table(name)

            elif action == 2:
                confirm = input(f"Вы уверены, что хотите удалить таблицу '{name}'? Это действие необратимо! (Y/N): ")
                if confirm == 'Y':
                    drop_table(name)

