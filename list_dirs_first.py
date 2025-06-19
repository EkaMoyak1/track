from pathlib import Path

# Список игнорируемых директорий
IGNORED_DIRS = {
    '.venv', '__pycache__', '.git', '.hg', '.svn',
    '.env', '.pyenv', 'env', 'venv', 'node_modules',
    '.idea', '.vscode', '.DS_Store'
}

# Имя выходного файла
OUTPUT_FILE = "structure.md"

def list_directory_contents(path='.', indent=''):
    """
    Рекурсивно выводит содержимое каталога:
    - сначала все папки, затем файлы
    - для папок load/tmp: показывает только первые 3 файла, остальные заменяются на ...
    Возвращает строку.
    """
    path = Path(path)
    name = path.name

    # Получаем список элементов
    items = sorted(path.iterdir(), key=lambda x: x.name)

    # Фильтруем игнорируемые элементы
    filtered_items = [item for item in items if item.name not in IGNORED_DIRS]

    # Разделяем папки и файлы
    dirs = [item for item in filtered_items if item.is_dir()]
    files = [item for item in filtered_items if item.is_file()]

    output = ""

    # Выводим папки
    for d in dirs:
        output += f"{indent}+ 📁 {d.name}/\n"
        output += list_directory_contents(d, indent + "  ")

    # Обработка файлов
    if name in ['load', 'tmp']:
        # Для папок load/tmp — выводим максимум 3 файла
        limited_files = files[:3]
        has_more = len(files) > 3

        for f in limited_files:
            output += f"{indent}  - 📄 {f.name}\n"
        if has_more:
            output += f"{indent}  - ...\n"
    else:
        # Все файлы для других папок
        for f in files:
            output += f"{indent}  - 📄 {f.name}\n"

    return output

if __name__ == '__main__':
    print("Сохраняю структуру каталогов в файл...\n")
    structure = list_directory_contents()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Структура проекта\n\n```\n")
        f.write(structure)
        f.write("\n```")

    print(f"✅ Структура успешно сохранена в файл: `{OUTPUT_FILE}`")