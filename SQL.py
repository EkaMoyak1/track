import sqlite3
from flask import flash


# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('date_source.db')
    return conn


# User related functions
def check_user_credentials(username, password):
    """Check if user credentials are valid"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teacher WHERE fio=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None


# Child related functions
def get_child_by_id(child_id, join_studio=False):
    """
    Get child information by ID
    :param child_id: ID of the child
    :param join_studio: Whether to join studio information
    :return: Child information
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if join_studio:
        query = """
            SELECT 
                spisok.id,
                spisok.fio,
                spisok.date_bd,
                spisok.age,
                spisok_in_studio.id as id_table
            FROM spisok 
            JOIN spisok_in_studio ON spisok.id = spisok_in_studio.id_spisok  
            WHERE spisok.id = ?
        """
    else:
        query = """
            SELECT 
                spisok.id,
                spisok.fio,
                spisok.date_bd,
                spisok.age
            FROM spisok 
            WHERE spisok.id = ?
        """

    cursor.execute(query, (child_id,))
    child = cursor.fetchone()
    conn.close()
    return child


def get_child_in_spisok(child_id):
    """Alias for get_child_by_id without studio join"""
    return get_child_by_id(child_id, join_studio=False)


def get_child_in_studya_by_id(field_id):
    """Get child information with studio details by studio ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            spisok.id,
            spisok.fio,
            spisok.date_bd,
            spisok.age,
            spisok_in_studio.napravlenie,
            spisok_in_studio.studio,
            spisok_in_studio.pedagog,
            spisok_in_studio.id as id_table
        FROM spisok_in_studio 
        JOIN spisok ON spisok_in_studio.id_spisok = spisok.id 
        WHERE spisok_in_studio.id = ?
    """, (field_id,))
    child = cursor.fetchone()
    conn.close()
    return child


# get_child_in_studya_by_id_copy is identical to get_child_in_studya_by_id, can be removed

# Events related functions
def get_events_by_id(event_id):
    """Get event by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events_table WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()
    return event


def get_events():
    """Get all events"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events_table ORDER BY name")
    events = cursor.fetchall()
    conn.close()
    return [[field.replace('"', "") if isinstance(field, str) else field for field in event] for event in events]


# Child list functions
def get_children_list(user, filter_flag=False, group_by=False, event_id=None):
    """
    Get list of children with optional filtering and grouping
    :param user: User making the request
    :param filter_flag: Whether to filter children with events
    :param group_by: Whether to group results
    :param event_id: Optional event ID to filter by
    :return: List of children
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = """
        SELECT 
            {columns}
        FROM spisok  
        {joins}
        {where}
        {group_by}
        ORDER BY fio
    """

    columns = """
        spisok_in_studio.id, 
        spisok.fio as fio, 
        spisok.date_bd, 
        spisok.age, 
        spr_napravlenie.name, 
        spr_studya.name, 
        teacher.fio as pedagog, 
        spisok.id
    """

    if group_by:
        columns = """
            max(spisok_in_studio.id), 
            spisok.fio as fio, 
            max(spisok.date_bd), 
            max(spisok.age), 
            max(spr_napravlenie.name), 
            max(spr_studya.name), 
            {teacher_column} as pedagog, 
            spisok.id
        """.format(
            teacher_column="max(teacher.fio)" if user == 'admin' else "teacher.fio"
        )

    joins = """
        JOIN spisok_in_studio ON spisok_in_studio.id_spisok = spisok.id
        LEFT JOIN spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
        LEFT JOIN spr_studya ON spisok_in_studio.studio = spr_studya.id
        {teacher_join} teacher ON spisok_in_studio.pedagog = teacher.id
    """.format(
        teacher_join="LEFT JOIN" if user == 'admin' else "JOIN"
    )

    where_clause = ""
    params = []

    if user != 'admin':
        where_clause = "WHERE teacher.fio = ?"
        params.append(user)

    if event_id:
        joins = """
            JOIN spisok_in_studio ON spisok_in_studio.id_spisok = spisok.id
            JOIN data_table ON data_table.id_spisok_in_studio = spisok_in_studio.id
            LEFT JOIN spr_napravlenie ON spisok_in_studio.napravlenie = spr_napravlenie.id
            LEFT JOIN spr_studya ON spisok_in_studio.studio = spr_studya.id
            {teacher_join} teacher ON spisok_in_studio.pedagog = teacher.id
        """.format(
            teacher_join="LEFT JOIN" if user == 'admin' else "JOIN"
        )

    if filter_flag:
        filter_condition = "spisok.id IN (SELECT id_spisok FROM data_table GROUP BY id_spisok)"
        if where_clause:
            where_clause += f" AND {filter_condition}"
        else:
            where_clause = f"WHERE {filter_condition}"

    group_by_clause = "GROUP BY spisok.fio, spisok.id" + (
        ", teacher.fio" if user != 'admin' and group_by else "") if group_by else ""

    query = base_query.format(
        columns=columns,
        joins=joins,
        where=where_clause,
        group_by=group_by_clause
    )

    print("Final query:", query)
    print("Params:", params)
    cursor.execute(query, params)
    children = cursor.fetchall()
    conn.close()
    return children


# The following functions can be replaced with calls to get_children_list:
def get_child_by_spisok():
    """Get all children ordered by name"""
    return get_children_list(user='admin')


def get_child_by_spisok_1(user, event):
    """Get children for specific event"""
    return get_children_list(user=user, event_id=event)


def get_children_in_spisok(user, filter_flag=False):
    """Get children list with optional filtering"""
    return get_children_list(user=user, filter_flag=filter_flag)


def get_children(user, filter_flag=False):
    """Alias for get_children_in_spisok"""
    return get_children_list(user=user, filter_flag=filter_flag)


def get_children_group(user, filter_flag=False):
    """Get grouped children list"""
    return get_children_list(user=user, filter_flag=filter_flag, group_by=True)


# Reference data functions
def get_napr():
    """Get all directions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spr_napravlenie")
    directions = cursor.fetchall()
    conn.close()
    return directions


def get_siudio():
    """Get all studios"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spr_studya")
    studios = cursor.fetchall()
    conn.close()
    return studios


def get_teacher(user_name=None):
    """Get teachers list"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_name == 'admin' or user_name is None:
        cursor.execute("SELECT * FROM teacher WHERE fio <> 'admin'")
    else:
        cursor.execute("SELECT * FROM teacher WHERE fio = ?", (user_name,))
    teachers = cursor.fetchall()
    conn.close()
    return teachers


# Competition data functions
def get_data_by_id_spisok(id_spisok, id_spisok_in_st='', user='admin'):
    """Get competition data by child ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if id_spisok_in_st == '':
        if user == 'admin':
            query = """
                SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                      events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file
                FROM data_table
                JOIN events_table ON data_table.id_events_table = events_table.id
                WHERE data_table.id_spisok = ? 
                ORDER BY data_table.id_spisok, events_table.result_date
            """
            params = (id_spisok,)
        else:
            query = """
                SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                      events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file
                FROM data_table
                JOIN events_table ON data_table.id_events_table = events_table.id
                JOIN spisok_in_studio ON data_table.id_spisok_in_studio = spisok_in_studio.id
                JOIN teacher ON spisok_in_studio.pedagog = teacher.id
                WHERE data_table.id_spisok = ? AND teacher.fio = ? 
                ORDER BY data_table.id_spisok, events_table.result_date
            """
            params = (id_spisok, user)
    else:
        query = """
            SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                  events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file
            FROM data_table
            JOIN events_table ON data_table.id_events_table = events_table.id
            JOIN spisok_in_studio ON spisok_in_studio.id_spisok = data_table.id_spisok
            WHERE data_table.id_spisok = ? AND spisok_in_studio.id = ?
            ORDER BY data_table.id_spisok, events_table.result_date
        """
        params = (id_spisok, id_spisok_in_st)

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


def get_data_by_id_spisok_kor(id_spisok, user):
    """Get short competition data by child ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if user == 'admin':
        query = """
            SELECT events_table.name, data_table.id, data_table.result, data_table.id_spisok_in_studio 
            FROM data_table
            JOIN events_table ON data_table.id_events_table = events_table.id
            WHERE data_table.id_spisok = ? 
            ORDER BY events_table.result_date
        """
        params = (id_spisok,)
    else:
        query = """
            SELECT events_table.name, data_table.id, data_table.result, data_table.id_spisok_in_studio 
            FROM data_table
            JOIN events_table ON data_table.id_events_table = events_table.id
            JOIN spisok_in_studio ON data_table.id_spisok_in_studio = spisok_in_studio.id
            JOIN teacher ON spisok_in_studio.pedagog = teacher.id
            WHERE data_table.id_spisok = ? AND teacher.fio = ?
            ORDER BY events_table.result_date
        """
        params = (id_spisok, user)

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


# CRUD operations
def save_in_date_table(request):
    """Save competition data"""
    try:
        id_spisok = request.form['id_spisok']
        id_events_table = request.form['id_events_table']
        doc_type = request.form['doc_type']
        saved_file_name = request.form['saved_file_name']
        field_id = request.form['field_id']
        file = request.files['fileInput']
        original_name = file.filename
        ext = original_name.split('.')[-1]
        saved_file_name += '.' + ext

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO data_table (id_spisok, id_spisok_in_studio, id_events_table, result, original_name, file)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_spisok, field_id, id_events_table, doc_type, original_name, saved_file_name))
        conn.commit()
        conn.close()
        flash('Запись успешно добавлена', 'success')
    except KeyError as e:
        flash(f'Ошибка: отсутствует поле {e}', 'error')


def update_in_data_table(request):
    """Update competition data"""
    record_id = request.form.get('record-id')
    id_spisok = request.form.get('id_spisok')
    id_events_table = request.form.get('id_events_table')
    result = request.form.get('id_doc_type')
    file = request.form.get('saved_file_name')
    original_name = request.form.get('original_file_name')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if not original_name:
            cursor.execute("""
                UPDATE data_table
                SET id_spisok = ?, id_events_table = ?, result = ?
                WHERE id = ?
            """, (id_spisok, id_events_table, result, record_id))
        else:
            cursor.execute("""
                UPDATE data_table
                SET id_spisok = ?, id_events_table = ?, result = ?, file = ?, original_name = ?
                WHERE id = ?
            """, (id_spisok, id_events_table, result, file, original_name, record_id))
        conn.commit()
        conn.close()
        flash('Запись успешно изменена', 'success')
    except KeyError as e:
        flash(f'Ошибка: отсутствует поле {e}', 'error')


def delete_in_data_table(record_id):
    """Delete competition data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM data_table WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        flash('Запись успешно удалена', 'success')
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')


def add_in_spisok_in_studio(request):
    """Add child to studio"""
    id_ch = request.form['fio']
    napravlenie = request.form['id_napr_table']
    studio = request.form['id_studio']
    pedagog = request.form['id_teacher']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO spisok_in_studio (id_spisok, napravlenie, studio, pedagog)
        VALUES (?, ?, ?, ?)
    """, (id_ch, napravlenie, studio, pedagog))
    conn.commit()
    conn.close()


def add_in_spisok(request):
    """Add new child"""
    fio = request.form['fio1']
    date_bd = request.form['date_bd']
    age = request.form['age']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO spisok (fio, date_bd, age)
        VALUES (?, ?, ?)
    """, (fio, date_bd, age))
    conn.commit()
    conn.close()
    return {'fio': fio, 'dr': date_bd, 'age': age}


def add_in_event(request):
    """Add new event"""
    name = request.form['name']
    opisanie = request.form['opisanie']
    srock = request.form['srock']
    resultat_date = request.form['resultat_date']
    level = request.form['level']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events_table (name, opisanie, srok_podachi_date, result_date, level)
            VALUES (?, ?, ?, ?, ?)
        """, (name, opisanie, srock, resultat_date, level))
        conn.commit()
        conn.close()
        flash('Конкурс успешно добавлен', 'success')
        return {"result": True}
    except Exception:
        conn.close()
        flash('Ошибка при записи конкурса', 'error')
        return {"result": False}


def edit_in_spisok(request, child_id):
    """Edit child information"""
    try:
        date_bd = request.form['date_bd']
        age = request.form['age']
        fio = request.form['fio']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE spisok
            SET date_bd=?, age=?, fio=?
            WHERE id = ?
        """, (date_bd, age, fio, child_id))
        conn.commit()
        conn.close()
        flash('Ребенок успешно изменен', 'success')
    except Exception:
        flash('Ошибка при записи', 'error')


def edit_in_spisok_studya(request, field_id):
    """Edit child information in studio"""
    try:
        date_bd = request.form['date_bd']
        age = request.form['age']
        napravlenie = request.form['id_napr_table']
        studio = request.form['id_studio']
        pedagog = request.form['id_teacher']

        child = get_child_in_studya_by_id(field_id)
        child_id = child[0]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update child info
        cursor.execute("""
            UPDATE spisok
            SET date_bd=?, age=?
            WHERE id = ?
        """, (date_bd, age, child_id))

        # Update studio info
        cursor.execute("""
            UPDATE spisok_in_studio
            SET napravlenie=?, studio=?, pedagog=?
            WHERE id = ?
        """, (napravlenie, studio, pedagog, field_id))

        conn.commit()
        conn.close()
        flash('Ребенок успешно изменен', 'success')
    except Exception:
        flash('Ошибка при записи', 'error')


def edit_in_events(request, event_id):
    """Edit event information"""
    try:
        name = request.form['name']
        opisanie = request.form['opisanie']
        srok_podachi_date = request.form['srok_podachi_date']
        result_date = request.form['result_date']
        level = request.form['level']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE events_table
            SET name=?, opisanie=?, srok_podachi_date=?, result_date=?, level=?
            WHERE id = ?
        """, (name, opisanie, srok_podachi_date, result_date, level, event_id))
        conn.commit()
        conn.close()
        flash('Конкурс успешно изменен', 'success')
    except Exception:
        flash('Ошибка при записи', 'error')


def delete_in_spisok(child_id):
    """Delete child from list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if child is in any studio
        cursor.execute('SELECT 1 FROM spisok_in_studio WHERE id_spisok = ?', (child_id,))
        if cursor.fetchone():
            flash('Запись не может быть удалена, так как ребенок числится в студии.', 'error')
        else:
            cursor.execute('DELETE FROM spisok WHERE id = ?', (child_id,))
            conn.commit()
            flash('Запись успешно удалена', 'success')

        conn.close()
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')


def delete_in_spisok_in_studya(field_id):
    """Delete child from studio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if child has competition records
        cursor.execute('SELECT 1 FROM data_table WHERE id_spisok = ?', (field_id,))
        if cursor.fetchone():
            flash('Запись не может быть удалена, так как ребенок участвует в конкурсе.', 'error')
        else:
            cursor.execute('DELETE FROM spisok_in_studio WHERE id = ?', (field_id,))
            conn.commit()
            flash('Запись успешно удалена', 'success')

        conn.close()
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')


def del_event(event_id):
    """Delete event"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if event has participants
        cursor.execute('SELECT 1 FROM data_table WHERE id_events_table = ?', (event_id,))
        if cursor.fetchone():
            flash('Запись не может быть удалена, так как есть дети, участвующие в этом конкурсе.', 'error')
        else:
            cursor.execute('DELETE FROM events_table WHERE id = ?', (event_id,))
            conn.commit()
            flash('Запись успешно удалена', 'success')

        conn.close()
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')


def add_super_user():
    """Add admin user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teacher (FIO, password)
        VALUES (?, ?)
    """, ('admin', 'cdomir2024'))
    conn.commit()
    conn.close()