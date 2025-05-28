from .db_helpers import get_db_connection


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
        SELECT {columns}
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


# Сохраняем все алиасы для совместимости
def get_child_by_spisok():
    return get_children_list(user='admin')


def get_child_by_spisok_1(user, event):
    return get_children_list(user=user, event_id=event)


def get_children_in_spisok(user, filter_flag=False):
    return get_children_list(user=user, filter_flag=filter_flag)


def get_children(user, filter_flag=False):
    return get_children_list(user=user, filter_flag=filter_flag)


def get_children_group(user, filter_flag=False):
    return get_children_list(user=user, filter_flag=filter_flag, group_by=True)