import sqlite3

# Соединение с базой данных (или создание новой, если ее нет)
conn = sqlite3.connect('date_source.db')
cursor = conn.cursor()

# Создание таблицы, если она не существует
sql_create = 'select * from data_table;'

cursor.execute(sql_create)
teacher = cursor.fetchall()

print(teacher)

# Добавление новой колонки 'original_name' в таблицу, если она не существует
try:
    cursor.execute("ALTER TABLE data_table ADD COLUMN original_name TEXT;")
    print("Колонка 'original_name' успешно добавлена.")
except sqlite3.OperationalError:
    print("Колонка 'original_name' уже существует или не удалось ее добавить.")

# Закрытие соединения с базой данных
conn.commit()
conn.close()

