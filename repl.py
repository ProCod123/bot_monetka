import re




text = """
import telebot
from telebot import types
import os
import time


from log_data import log_data_to_file
from work_with_exel import get_task, get_name, file_zapusk, run_vba_macro
from export import insert_data_to_excel, xlsm_to_pdf
from workers import DF, ROR, RP_MSK, RP_SPB, ID
from create import path_to_folder, destination_folder, create_task_folder, start_update
import base

bot = telebot.TeleBot('5820874061:AAGGpfqaRZkV7ZRHrezJEq41fdIeJ85KeUk')

form_data = {}


@bot.message_handler(commands=['start'])
def start(message):

    global values, keyboard

    # Отображаем значок загрузки
    bot.send_chat_action(message.chat.id, 'typing')
    messagetoedit = bot.send_message(message.chat.id, 'Подождите...')
    
    values = get_task(file_zapusk)
    create_task_folder(path_to_folder, values)

    # Настраиваем минимальную периодичность обновлений 
    if form_data.get('время_обновления'):
        difference = time.time() - form_data['время_обновления']
        if difference < 60:
            pass
        else:
            values = get_task(file_zapusk)
            form_data['время_обновления'] = time.time()
    else:
        values = get_task(file_zapusk)
        form_data['время_обновления'] = time.time()

    name = get_name(message.chat.id)

    if name is None:
        bot.send_message(message.chat.id, 'Ваш ID отсутствует в списке! Обратитесь к администратору.')
    else:
        bot.delete_message(message.chat.id, message_id=messagetoedit.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for adress in values.get(name):
            keyboard.add(telebot.types.InlineKeyboardButton(adress.split(', ')[-1], callback_data=name + ',' + str(values.get(name).index(adress))))
        # Отправка приветственного сообщения с инлайн-клавиатурой
        bot.send_message(message.chat.id, 'Требуется предоставить АПО по объектам:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    print(call.data)
    global keyboard_folder
    folder = None

    # Получаем ID пользователя
    user_id = call.message.chat.id

    # Если для пользователя нет данных, создаем словарь для него
    if user_id not in form_data:
        form_data[user_id] = {}
    try:
        if len(call.data.split(',')) > 1:
            form_data[user_id]['name'] = call.data.split(',')[0]
            base.update_form_data(user_id, {'name' : call.data.split(',')[0]})
            form_data[user_id]['number'] = int(call.data.split(',')[1])
            form_data[user_id]['adr'] = values.get(form_data[user_id]['name'])[form_data[user_id]['number']]
            form_data[user_id]['филиал'] = form_data[user_id]['adr'].split(' ')[1]
            send_choice_message(call.message.chat.id)

        if call.data == 'begin_apo':
            # Функция для отправки первого вопроса
            start_form(call.message)

        elif call.data == 'load_photo':
            keyboard_folder = telebot.types.InlineKeyboardMarkup()
            keyboard_folder.row(telebot.types.InlineKeyboardButton('1 Схема замеров помещения', callback_data='1'))
            keyboard_folder.row(telebot.types.InlineKeyboardButton('2 Схема замеров фасада гл. вход', callback_data='2'))
            keyboard_folder.row(telebot.types.InlineKeyboardButton('3 Схема замеров фасада прав. стор.', callback_data='3'))
            keyboard_folder.row(telebot.types.InlineKeyboardButton('4 Схема замеров фасада левая стор.', callback_data='4'))
            keyboard_folder.row(telebot.types.InlineKeyboardButton('5 Схема размеров фасада обр. стор.', callback_data='5'))
            keyboard_folder.row(telebot.types.InlineKeyboardButton('6 Ситуационный план', callback_data='6'))
            keyboard_folder.row(telebot.types.InlineKeyboardButton('7 Конструктивная схема помещения', callback_data='7'))
            keyboard_folder.row(telebot.types.InlineKeyboardButton('8 Схема предварительного зонир.', callback_data='8'))
            keyboard_folder.add(telebot.types.InlineKeyboardButton('9 Схема кровли', callback_data='9'))
            keyboard_folder.add(telebot.types.InlineKeyboardButton('Назад', callback_data='back_to_main'))
            bot.send_message(call.message.chat.id, f'Выбран объект: {form_data[user_id]['adr']}. Выберите тип фото:', reply_markup=keyboard_folder)
   
        elif call.data == 'back_to_main':
            bot.send_message(call.message.chat.id, f'Выберите действие по объекту: {form_data[user_id]['adr']}.', reply_markup=keyboard_2)

        elif call.data == 'back':
            start(call.message)

        elif call.data == '1':
            folder = '1 Схема замеров помещения'
        elif call.data == '2':
            folder = '2 Схема замеров фасада главный вход'
        elif call.data == '3':
            folder = '3 Схема замеров фасада правая сторона'
        elif call.data == '4':
            folder = '4 Схема замеров фасада левая сторона'
        elif call.data == '5':
            folder = '5 Схема размеров фасада обратная сторона'
        elif call.data == '6':
            folder = '6 Ситуационный план'
        elif call.data == '7':
            folder = '7 Конструктивная схема помещения'
        elif call.data == '8':
            folder = '8 Схема предварительного зонирования'
        elif call.data == '9':
            folder = '9 Схема кровли'

        # Вопрос о дальнейшей отправке
        if call.data == 'Yes':
            bot.send_message(call.message.chat.id, 'Выберите тип фото:', reply_markup=keyboard_folder)
        elif call.data == 'No':

            # Если пользователь не будет больше подгружать фото 
            # Запуск макроса собирающего фото
            path_script = os.path.abspath(get_path_to_apo(call.message.chat.id)).replace('\\', '/')
            # Отображаем значок загрузки
            bot.send_chat_action(call.message.chat.id, 'typing')
            messagetoedit = bot.send_message(call.message.chat.id, 'Подождите...')

            run_vba_macro(path_script, 'module1', 'AddPhotosToSheet')

            # удаляем сообщение подождите...
            bot.delete_message(call.message.chat.id, message_id=messagetoedit.message_id)

            keyboard_approve = telebot.types.InlineKeyboardMarkup()
            keyboard_approve.add(telebot.types.InlineKeyboardButton('Согласовать', callback_data='approve'), telebot.types.InlineKeyboardButton('Пропустить', callback_data='not_approve'))
            bot.send_message(call.message.chat.id, 'Для добавления подписи в документ нажмите Согласовать', reply_markup=keyboard_approve)
        
        elif call.data == 'approve':
            # Вставляем подпись
            file_name = os.path.abspath(get_path_to_apo(call.message.chat.id)).replace('\\', '/')
            print(file_name)
            run_vba_macro(file_name, 'module2', 'InsertImage')

            bot.send_message(call.message.chat.id, 'Подпись добавлена!')
            
            # Конвертируем файл в ПДФ
            xlsm_to_pdf(file_name)
            # Находим путь к созданному ПДФ
            file_pdf = file_name.split('.xlsm')[0] + '.pdf'
            # Отправляем файл
            send_file_telegram(file_pdf, call.message.chat.id)

            bot.send_message(call.message.chat.id, 'Требуется предоставить АПО по объектам:', reply_markup=keyboard)

        elif call.data == 'not_approve':
            file_name = get_path_to_apo(call.message.chat.id)
            send_file_telegram(file_name, call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Требуется предоставить АПО по объектам:', reply_markup=keyboard)

        if folder is not None:
            form_data[user_id]['objects_path'] = path_to_folder  + form_data[user_id]['adr'] + '\\Фото\\' + folder
            bot.send_message(call.message.chat.id, 'Отправьте фото! Путь к папке: ' + form_data[user_id]['objects_path'])
    except Exception as e:
        print(e)
        start(call.message)

# Обработка отправленного фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Сохранение фото
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохранение файла в папку объекта
    filepath = os.path.join(form_data[message.chat.id]['objects_path'], file_info.file_path.split('/')[-1])
    with open(filepath, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Запрос на продолжение
    keyboard_foto = telebot.types.InlineKeyboardMarkup()
    keyboard_foto.add(telebot.types.InlineKeyboardButton('Да', callback_data='Yes'), telebot.types.InlineKeyboardButton('Нет', callback_data='No'))
    bot.send_message(message.chat.id, 'Хотите загрузить еще фото?', reply_markup=keyboard_foto)


# 1. Владелец 
def start_form(message):
    # form_data.clear()  # Очищаем данные формы перед началом
    # Добавляем филиал в словарь
    user_id = message.chat.id
    # update_form_data(user_id, data)
    form_data[user_id]['адрес'] = ' '.join(form_data[user_id]['adr'].split(' ')[1:])
    # Находим полние имя РП
    for text in (RP_MSK + RP_SPB):
        if form_data[user_id]['name'] in text:
            form_data[user_id]['рп'] = text
    if form_data[user_id]['филиал'] == 'МСК':
        form_data[user_id]['председатель'] = DF[0]
        form_data[user_id]['член_ком1'] = ROR[0]
    elif form_data[user_id]['филиал'] == 'СПБ':
        form_data[user_id]['председатель'] = DF[1]
        form_data[user_id]['член_ком1'] = ROR[1]

    bot.send_message(
        message.chat.id,
        'Площадь помещения:',
        reply_markup=create_keyboard_with_skip_and_back('Пропустить'),
    )
    bot.register_next_step_handler(message, process_area)


# Функция для обработки ответа на вопрос о площади помещения
def process_area(message):
    if message.text == 'Пропустить':
        form_data[message.chat.id]['площадь_помещения'] = 'Пропущено'
        ask_floor(message)
        return
    form_data[message.chat.id]['площадь_помещения'] = message.text
    ask_floor(message)

# Функция для отправки вопроса об этаже
def ask_floor(message):
    bot.send_message(
        message.chat.id,
        'Расположено на этаже:',
        reply_markup=create_keyboard_with_skip_and_back('Пропустить', 'Назад'),
    )
    bot.register_next_step_handler(message, process_floor)

# Функция для обработки ответа на вопрос об этаже
def process_floor(message):
    if message.text == 'Пропустить':
        form_data[message.chat.id]['этаж'] = 'Пропущено'
        ask_building_floors(message)
        return
    elif message.text == 'Назад':
        if 'этаж' in form_data:
            del form_data[message.chat.id]['этаж']
        start_form(message)
        return
    form_data[message.chat.id]['этаж'] = message.text
    ask_building_floors(message)

# Функция для отправки вопроса о этажности здания
def ask_building_floors(message):
    bot.send_message(
        message.chat.id,
        'Этажность всего здания:',
        reply_markup=create_keyboard_with_skip_and_back('Пропустить', 'Назад'),
    )
    bot.register_next_step_handler(message, process_building_floors)

# Функция для обработки ответа на вопрос о этажности здания
def process_building_floors(message):
    if message.text == 'Пропустить':
        form_data[message.chat.id]['этажность'] = 'Пропущено'
        askobjecttype(message)
        return
    elif message.text == 'Назад':
        if 'этажность' in form_data:
            del form_data[message.chat.id]['этажность']
        ask_floor(message)
        return
    form_data[message.chat.id]['этажность'] = message.text
    askobjecttype(message)

# Функция для отправки вопроса о типе объекта
def askobjecttype(message): 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) 
    markup.add(types.KeyboardButton('Встроен./встроен.-пристроен.')) 
    markup.add(types.KeyboardButton('Торг. Центр')) 
    markup.add(types.KeyboardButton('Цоколь/подвал. Этаж')) 
    markup.add(types.KeyboardButton('Иные объекты')) 
    markup.add(types.KeyboardButton('Пропустить'), types.KeyboardButton('Назад')) 
    bot.send_message(message.chat.id, '12. Тип объекта:', reply_markup=markup) 
    bot.register_next_step_handler(message, processobjecttype)

 
def processobjecttype(message): 
    if message.text == 'Пропустить': 
        form_data[message.chat.id]['тип_объекта'] = 'Пропущено' 
        ask_basement_use_2(message) 
        return 
    elif message.text == 'Назад': 
        if 'тип_объекта' in form_data: 
            del form_data[message.chat.id]['тип_объекта']
            ask_building_floors(message) 
        return 
    form_data[message.chat.id]['тип_объекта'] = message.text 
    ask_basement_use_2(message)


# Функция для отправки вопроса о помещении
def ask_basement_use_2(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('Да'))
    markup.add(types.KeyboardButton('Нет'))
    markup.add(types.KeyboardButton('Пропустить'), types.KeyboardButton('Назад'))
    bot.send_message(
        message.chat.id,
        'Предполагается использование подвальных помещений:',
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_basement_use_2)

# Функция для обработки ответа на вопрос о использовании подвальных помещений
def process_basement_use_2(message):
    if message.text == 'Пропустить':
        form_data[message.chat.id]['использование_подвала'] = 'Пропущено'
        ask_comment_6(message)
        return
    elif message.text == 'Назад':
        if 'использование_подвала' in form_data:
            del form_data[message.chat.id]['использование_подвала']
        askobjecttype(message)  # Укажите, какой вопрос требуется
        return
    form_data[message.chat.id]['использование_подвала'] = message.text
    ask_comment_6(message)

# Функция для отправки комментария
def ask_comment_6(message):
    bot.send_message(
        message.chat.id,
        'Комментарий:',
        reply_markup=create_keyboard_with_skip_and_back('Пропустить', 'Назад'),
    )
    bot.register_next_step_handler(message, process_comment_6)



    """

a = text.replace("data)['", "{'[")
new = a.replace("'] = ", "]' : )")
print(new)
