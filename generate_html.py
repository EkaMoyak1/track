import sqlite3

def fetch_data(query):
    db_lp = sqlite3.connect('date_source.db')
    cursor_db = db_lp.cursor()
    cursor_db.execute(query)
    rows = cursor_db.fetchall()
    cursor_db.close()
    db_lp.close()
    return rows

def generate_html(file_name, headers, rows):
    # Открываем файл-шаблон в режиме чтения
    with open(file_name.replace('.html', '_template.html'), 'r', encoding='utf-8') as template:
        html_content = template.read()

    # Создаем строки таблицы из данных
    rows_html = ""
    for row in rows:
        row_html = "<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>\n"
        rows_html += row_html

    # Заменяем маркер {{ rows }} на строки таблицы
    html_content = html_content.replace("{{ rows }}", rows_html)

    # Записываем окончательный HTML в файл
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    # Генерация HTML для spisok
    spisok_query = "SELECT * FROM spisok;"
    spisok_data = fetch_data(spisok_query)
    generate_html('spisok.html', ["ID", "ФИО", "Дата рождения", "Возраст", "Направление", "Студия", "Педагог"], spisok_data)

    # Генерация HTML для events_table
    events_query = "SELECT * FROM events_table;"
    events_data = fetch_data(events_query)
    generate_html('events_table.html', ["ID", "Название", "Описание", "Срок подачи", "Дата результата"], events_data)

    # Генерация HTML для data_table
    data_query = "SELECT * FROM data_table;"
    data_data = fetch_data(data_query)
    generate_html('data_table.html', ["ID", "ID Списка", "ID События", "Результат"], data_data)

if __name__ == "__main__":
    main()