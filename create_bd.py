from  sql_utils import db_helpers, user_db
import sqlite3

def create_tables():
    db_lp = db_helpers.get_db_connection()
    db_lp.execute("PRAGMA foreign_keys = ON")  # Включаем внешние ключи
    cursor_db = db_lp.cursor()

    # spisok - список детей
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

    # spisok_in_studio - дети в студиях
    sql_create_spisok_in_studio = '''
    CREATE TABLE IF NOT EXISTS spisok_in_studio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_spisok INTEGER NOT NULL,
        napravlenie INTEGER NOT NULL,
        studio INTEGER NOT NULL,
        pedagog INTEGER NOT NULL,
        FOREIGN KEY (id_spisok) REFERENCES spisok(id) ON DELETE RESTRICT,
        FOREIGN KEY (napravlenie) REFERENCES spr_napravlenie(id) ON DELETE RESTRICT,
        FOREIGN KEY (studio) REFERENCES spr_studya(id) ON DELETE RESTRICT,
        FOREIGN KEY (pedagog) REFERENCES teacher(id) ON DELETE RESTRICT
    );
    '''
    cursor_db.execute(sql_create_spisok_in_studio)
    db_lp.commit()

    # event_type - типы конкурсов
    sql_create_event_type = '''
    CREATE TABLE IF NOT EXISTS event_type (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    '''
    cursor_db.execute(sql_create_event_type)
    db_lp.commit()

    # events_table - справочник конкурсов
    sql_create_events_table = '''
    CREATE TABLE IF NOT EXISTS events_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        opisanie TEXT,
        srok_podachi_date DATE,
        result_date DATE,
        level TEXT,
        type_event_id INTEGER,
        FOREIGN KEY (type_event_id) REFERENCES event_type(id)
    );
    '''
    cursor_db.execute(sql_create_events_table)
    db_lp.commit()

    # data_table - участие детей в конкурсах
    sql_create_data_table = '''
    CREATE TABLE IF NOT EXISTS data_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_spisok INTEGER NOT NULL,
        id_spisok_in_studio INTEGER NOT NULL,
        id_events_table INTEGER NOT NULL,
        result TEXT,
        original_name TEXT,
        file TEXT,
        date_otcheta DATE,
        FOREIGN KEY (id_spisok) REFERENCES spisok(id) ON DELETE RESTRICT,
        FOREIGN KEY (id_spisok_in_studio) REFERENCES spisok_in_studio(id) ON DELETE RESTRICT,
        FOREIGN KEY (id_events_table) REFERENCES events_table(id) ON DELETE RESTRICT
    );
    '''
    cursor_db.execute(sql_create_data_table)
    db_lp.commit()

    # spr_napravlenie - справочник направлений
    sql_create_spr_napravlenie = '''
    CREATE TABLE IF NOT EXISTS spr_napravlenie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    '''
    cursor_db.execute(sql_create_spr_napravlenie)
    db_lp.commit()

    # spr_studya - справочник студий
    sql_create_spr_studya = '''
    CREATE TABLE IF NOT EXISTS spr_studya (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    '''
    cursor_db.execute(sql_create_spr_studya)
    db_lp.commit()

    # studyas_in_napravlenie - связь студий и направлений
    sql_create_studyas_in_napravlenie = '''
    CREATE TABLE IF NOT EXISTS studyas_in_napravlenie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_studya INTEGER NOT NULL,
        id_napravlenie INTEGER NOT NULL,
        UNIQUE(id_studya, id_napravlenie),
        FOREIGN KEY (id_studya) REFERENCES spr_studya(id) ON DELETE CASCADE,
        FOREIGN KEY (id_napravlenie) REFERENCES spr_napravlenie(id) ON DELETE CASCADE
    );
    '''
    cursor_db.execute(sql_create_studyas_in_napravlenie)
    db_lp.commit()

    # teacher - педагоги
    sql_create_teacher = '''
    CREATE TABLE IF NOT EXISTS teacher (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        FIO TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    '''
    cursor_db.execute(sql_create_teacher)
    db_lp.commit()

    # user_settings - настройки пользователей
    sql_create_user_settings = '''
    CREATE TABLE IF NOT EXISTS user_settings (
        id TEXT PRIMARY KEY,
        user TEXT NOT NULL,
        year_1 INTEGER DEFAULT 2024,
        year_2 INTEGER DEFAULT 2025
    );
    '''
    cursor_db.execute(sql_create_user_settings)
    db_lp.commit()

    # Заполнение начальных данных в event_type
    event_types = ["",
        "НПК", "НИР", "Творческий", "Олимпиада",
        "Викторина", "Мастер класс", "Хакатон"
    ]
    for name in event_types:
        cursor_db.execute('INSERT OR IGNORE INTO event_type (name) VALUES (?)', (name,))
    db_lp.commit()

    cursor_db.close()
    db_lp.close()


def show_tbl(table):
    conn = db_helpers.get_db_connection()
    conn.row_factory = sqlite3.Row  # Чтобы получать строки как словари
    cursor = conn.cursor()

    try:
        cursor.execute(f'SELECT * FROM {table}')
        rows = cursor.fetchall()

        if not rows:
            print(f"\n[Таблица '{table}'] пуста.\n")
            return

        # Преобразуем Row в словари
        data = [dict(row) for row in rows]

        # Выводим красиво
        print(f"\n[Таблица: {table}]")
        print("-" * 50)

        # Выводим заголовки колонок
        headers = data[0].keys()
        print(" | ".join(headers))

        # Выводим каждую строку
        for row in data:
            print(" | ".join(str(v) for v in row.values()))

        print("-" * 50 + "\n")

    except sqlite3.OperationalError as e:
        print(f"[Ошибка] Не удалось прочитать таблицу '{table}': {e}")
    finally:
        conn.close()


def drop_table(name):
    db_lp = db_helpers.get_db_connection()
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
    db_lp =db_helpers.get_db_connection()
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
    db_lp = db_helpers.get_db_connection()
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


if __name__ == '__main__':
    # create_tables()1
    # SQL.add_super_user()
    # show_tbl('teacher')
    print('1 - show')
    print('2 - drop')
    print('4 - create bd')

    rej = int(input('выберите режим '))


    if rej == 4:
        create_tables()
        user_db.add_super_user()
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
        print('10 - type_event')
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
        elif tab == 10:
            name = 'event_type'

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

