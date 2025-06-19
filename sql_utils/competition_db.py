from .db_helpers import get_db_connection

def get_data_by_id_spisok(id_spisok, id_spisok_in_st='', user='admin'):
    conn = get_db_connection()
    cursor = conn.cursor()

    if id_spisok_in_st == '':
        if user == 'admin':
            query = """
                SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                      events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file, data_table.date_otcheta
                FROM data_table
                JOIN events_table ON data_table.id_events_table = events_table.id
                WHERE data_table.id_spisok = ? 
                ORDER BY data_table.id_spisok, events_table.result_date
            """
            params = (id_spisok,)
        else:
            query = """
                SELECT data_table.id, data_table.id_spisok, data_table.id_events_table, data_table.result,
                      events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file,  data_table.date_otcheta
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
                  events_table.name, events_table.opisanie, events_table.srok_podachi_date, events_table.result_date, original_name, file, data_table.date_otcheta
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
    conn = get_db_connection()
    cursor = conn.cursor()

    if user == 'admin':
        query = """
            SELECT events_table.name, data_table.id, data_table.result, data_table.id_spisok_in_studio , data_table.date_otcheta
            FROM data_table
            JOIN events_table ON data_table.id_events_table = events_table.id
            WHERE data_table.id_spisok = ? 
            ORDER BY events_table.result_date
        """
        params = (id_spisok,)
    else:
        query = """
            SELECT events_table.name, data_table.id, data_table.result, data_table.id_spisok_in_studio , data_table.date_otcheta
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