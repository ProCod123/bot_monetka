import os
import shutil
from workers import ID
from work_with_exel import get_task, file_zapusk


path_to_folder = os.path.abspath("..\\" + os.curdir) + '\АПО\\'


x = get_task(file_zapusk)


# Создаем папку РП если ее нет
def create_rp_folder(path_to_folder, sername):
    for item in sername:
        if os.path.exists(path_to_folder + item):
            pass
        else:
            os.mkdir(path_to_folder + item)


# create_rp_folder(path_to_folder, ID)


# Создаем папку объекта если ее нет
def create_task_folder(path_to_folder, tasks):
    for name in tasks:
        objects = tasks.get(name)
        for i in objects:
            task_folder = path_to_folder + name + '\\' + i
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

                apo_name = 'АПО ' + ' '.join(task_folder.split(' ')[1:]) + '.xlsm'
                shutil.copy(os.path.abspath("..\\" + os.curdir) + '\АПО.xlsm', task_folder + '/' + apo_name)


# create_task_folder(path_to_folder, x)
