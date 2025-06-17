import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TableInfo:
    name: str
    columns: Dict[str, str]  # {column_name: column_type}


def get_db_structure(db_path: str) -> Dict[str, TableInfo]:
    """Получить структуру базы данных в виде словаря таблиц"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем список всех таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    structure = {}

    for table in tables:
        table_name = table[0]
        if table_name == 'sqlite_sequence':
            continue

        # Получаем информацию о колонках таблицы
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        columns_dict = {}
        for column in columns:
            col_name = column[1]
            col_type = column[2]
            columns_dict[col_name] = col_type

        structure[table_name] = TableInfo(table_name, columns_dict)

    conn.close()
    return structure


def compare_structures(db1: Dict[str, TableInfo], db2: Dict[str, TableInfo]) -> None:
    """Сравнить две структуры баз данных и вывести различия"""
    all_tables = set(db1.keys()).union(set(db2.keys()))

    differences_found = False

    for table in sorted(all_tables):
        table1 = db1.get(table)
        table2 = db2.get(table)

        if table1 is None:
            print(f"Таблица '{table}' есть во второй базе, но отсутствует в первой")
            differences_found = True
            continue

        if table2 is None:
            print(f"Таблица '{table}' есть в первой базе, но отсутствует во второй")
            differences_found = True
            continue

        # Сравниваем колонки
        all_columns = set(table1.columns.keys()).union(set(table2.columns.keys()))
        columns_differ = False

        for column in sorted(all_columns):
            type1 = table1.columns.get(column)
            type2 = table2.columns.get(column)

            if type1 is None:
                print(f"Таблица '{table}': столбец '{column}' есть во второй базе, но отсутствует в первой")
                columns_differ = True
                continue

            if type2 is None:
                print(f"Таблица '{table}': столбец '{column}' есть в первой базе, но отсутствует во второй")
                columns_differ = True
                continue

            if type1 != type2:
                print(
                    f"Таблица '{table}': столбец '{column}' имеет разные типы: первая база - {type1}, вторая база - {type2}")
                columns_differ = True

        if columns_differ:
            differences_found = True

    if not differences_found:
        print("Структуры баз данных идентичны")


if __name__ == "__main__":
    db1_path = input("Введите путь к первой базе данных SQLite: ").strip()
    db2_path = input("Введите путь ко второй базе данных SQLite: ").strip()

    print("\nСравниваем структуры баз данных...\n")

    try:
        db1_structure = get_db_structure(db1_path)
        db2_structure = get_db_structure(db2_path)

        compare_structures(db1_structure, db2_structure)
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")