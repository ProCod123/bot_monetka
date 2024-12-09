import os
import json
import time
import schedule

def get_last_modified_date(folder_path):
    """
    Возвращает словарь с данными о файлах, группируя их по объектам,
    игнорируя папки ниже уровня объекта.
    """
    last_modified = {}
    for root, _, files in os.walk(folder_path):
        parts = os.path.relpath(root, folder_path).split(os.sep)
        if len(parts) > 1: # Игнорируем корень и папки ниже уровня объекта
            object_name = parts[0]
            if object_name not in last_modified:
                last_modified[object_name] = {}
            for file in files:
                item_path = os.path.join(root, file)
                modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(item_path)))
                last_modified[object_name][file] = modified_time
        else: #обрабатываем файлы в корневой папке
            if "объект" not in last_modified:
                last_modified["объект"] = {}
            for file in files:
                item_path = os.path.join(root, file)
                modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(item_path)))
                last_modified["объект"][file] = modified_time


    return last_modified

# def process_folders(main_folder_path, output_json_path):
#     """
#     Обрабатывает подпапки, собирает данные и сохраняет их в JSON файл.
#     """
#     all_data = {}
#     for folder_name in os.listdir(main_folder_path):
#         employee_folder_path = os.path.join(main_folder_path, folder_name)
#         if os.path.isdir(employee_folder_path):
#             all_data[folder_name] = get_last_modified_date(employee_folder_path)
#     with open(output_json_path, 'w', encoding='utf-8') as json_file:
#         json.dump(all_data, json_file, indent=4, ensure_ascii=False)

# def main(main_folder_path, output_json_path):
#     """Основная функция, запускающая обработку и планирование."""
#     process_folders(main_folder_path, output_json_path)
#     schedule.every().hour.do(lambda: process_folders(main_folder_path, output_json_path))

#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# if __name__ == "__main__":
#     main_folder_path = 'C:/Users/user/Desktop/раб/АПО'
#     output_json_path = 'C:/Users/user/Desktop/раб/bot/tt.json'

#     # проверка существования папки
#     if not os.path.exists(main_folder_path):
#       print(f"Ошибка: папка {main_folder_path} не существует.")
#       exit()

    main(main_folder_path, output_json_path)

x = get_last_modified_date('C:/Users/user/Desktop/раб/АПО')
print(x)
