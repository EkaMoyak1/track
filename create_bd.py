import sqlite3
import SQL

def create_tables():
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    sql_create = '''CREATE TABLE if NOT exists spisok(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fio TEXT NOT NULL,
                    date_bd DATE NOT NULL,
                    age INT,
                    napravlenie INTEGER NOT NULL,
                    studio INTEGER NOT NULL,
                    pedagog INTEGER NOT NULL
                    );'''

    cursor_db.execute(sql_create)
    db_lp.commit()

    sql_create = '''CREATE TABLE if NOT exists events_table(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    opisanie TEXT,
                    srok_podachi_date DATE,
                    result_date DATE
                    );'''

    cursor_db.execute(sql_create)
    db_lp.commit()

    sql_create = '''CREATE TABLE if NOT exists data_table(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_spisok int NOT NULL,
                    id_events_table int NOT NULL,
                    result TEXT,
                    original_name TEXT,
                    file TEXT
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

if __name__ == '__main__':
    # create_tables()
    SQL.add_super_user()
    show_tbl('teacher')
    # show_tbl('spisok')
