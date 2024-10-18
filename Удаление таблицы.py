import sqlite3

# Подключение к базе данных (или создание новой базы данных)
connection = sqlite3.connect('date_source.db')
cursor = connection.cursor()

# Удаление таблицы events_table
cursor.execute('DROP TABLE IF EXISTS events_table')

# Сохранение изменений и закрытие соединения
connection.commit()
connection.close()