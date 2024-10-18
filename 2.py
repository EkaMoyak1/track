
import sqlite3
import turtle
turtle.circle(100, extent=180)

# Подключение к базе данных
db_lp = sqlite3.connect('date_source.db')
cursor_db = db_lp.cursor()

# Выполнение запроса для получения структуры таблицы
cursor_db.execute("PRAGMA table_info(spisok)")

# Получение всех результатов
columns = cursor_db.fetchall()

# Вывод структуры таблицы
print("Структура таблицы spisok:")
for column in columns:
    print(f"Имя: {column[1]}, Тип: {column[2]}, NOT NULL: {column[3]}, PRIMARY KEY: {column[5]}")


db_lp = sqlite3.connect('date_source.db')
cursor_db = db_lp.cursor()
cursor_db.execute("SELECT * FROM spisok" )
child = cursor_db.fetchall()
cursor_db.close()
db_lp.close()
print(*child)