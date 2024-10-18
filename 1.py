import sqlite3
db_lp = sqlite3.connect('date_source.db')
cursor_db = db_lp.cursor()
sql_create = 'ALTER TABLE spisok ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT;'

cursor_db.execute(sql_create)
db_lp.commit()

cursor_db.close()
db_lp.close()