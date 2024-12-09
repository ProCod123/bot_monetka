import os
import shutil

# import time
# import threading
# import schedule





# расположение папки АПО с обновляемой ботом
path_to_folder = os.path.abspath("..\\" + os.curdir) + '\АПО\\'
destination_folder = 'C:/Users/user/Desktop/раб/Объекты'


# Создаем папку объекта если ее нет
def create_task_folder(path_to_folder, tasks):
    for name in tasks:
        objects = tasks.get(name)
        for i in objects:
            task_folder = path_to_folder + '\\' + i
            if os.path.exists(task_folder):
                pass
            else:
                os.mkdir(task_folder)
                os.mkdir(task_folder + '\Фото')
                os.mkdir(task_folder + '\Фото\\1 Схема замеров помещения')
                os.mkdir(task_folder + '\Фото\\2 Схема замеров фасада главный вход')
                os.mkdir(task_folder + '\Фото\\3 Схема замеров фасада правая сторона')
                os.mkdir(task_folder + '\Фото\\4 Схема замеров фасада левая сторона')
                os.mkdir(task_folder + '\Фото\\5 Схема размеров фасада обратная сторона')
                os.mkdir(task_folder + '\Фото\\6 Ситуационный план')
                os.mkdir(task_folder + '\Фото\\7 Конструктивная схема помещения')
                os.mkdir(task_folder + '\Фото\\8 Схема предварительного зонирования')
                os.mkdir(task_folder + '\Фото\\9 Схема кровли')

                apo_name = 'АПО ' + ' '.join(task_folder.split(' ')[1:]) + '.xlsm'
                shutil.copy(os.path.abspath("..\\" + os.curdir) + '\АПО.xlsm', task_folder + '/' + apo_name)


# create_task_folder(path_to_folder, x)



def update_folder(source_folder, destination_folder):
    """
    Сравнивает содержимое двух папок и обновляет файлы и папки в целевой папке,
    если дата изменения в исходной папке новее.
    """
    for root, _, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)
        destination_path = os.path.join(destination_folder, relative_path)

        # Создаем путь, если его нет.
        os.makedirs(destination_path, exist_ok=True)

        for file_name in files:
            source_file_path = os.path.join(root, file_name)
            destination_file_path = os.path.join(destination_path, file_name)

            try:
                source_mtime = os.path.getmtime(source_file_path)
                if os.path.exists(destination_file_path):
                    destination_mtime = os.path.getmtime(destination_file_path)
                    if source_mtime > destination_mtime:
                        print(f"Обновляю: {destination_file_path}")
                        shutil.copy2(source_file_path, destination_file_path) 
                else:
                    print(f"Копирую: {destination_file_path}")
                    shutil.copy2(source_file_path, destination_file_path)
            except OSError as e:
                print(f"Ошибка при обработке файла {file_name}: {e}")

            except FileNotFoundError as e:
                print(f"Ошибка: Файл {source_file_path} не найден: {e}")


def start_update(path_to_folder, destination_folder):

    for folder in os.listdir(path_to_folder):
        path_destination_folder = destination_folder + '/' + folder + '/Акты/АПО'
        source_folder = path_to_folder + folder

        # Проверка существования папок
        if not os.path.exists(source_folder):
            print(f"Ошибка: Исходная папка '{source_folder}' не существует.")
            exit()
        if not os.path.exists(path_destination_folder):
            print(f"Ошибка: Целевая папка '{path_destination_folder}' не существует.")
            exit()

        update_folder(source_folder, path_destination_folder)

    print("Обновление завершено.")

start_update(path_to_folder, destination_folder)


# def start_update_task(source_folder, destination_folder):
#     schedule.every(1).minutes.do(lambda: start_update(source_folder, destination_folder))
#     while True:
#         print(1)
#         schedule.run_pending()
#         time.sleep(2)



# # Запуск задачи обновления в отдельном потоке
# update_thread = threading.Thread(target=start_update_task, args=(path_to_folder, destination_folder))
# update_thread.daemon = True # Позволяет завершить программу, даже если поток работает
# update_thread.start()
