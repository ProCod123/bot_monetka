import telebot
from telebot import types
import os
import time


from log_data import log_data_to_file
from work_with_exel import get_task, get_name, file_zapusk, run_vba_macro
from export import insert_data_to_excel, xlsm_to_pdf
from workers import DF, ROR, RP_MSK, RP_SPB, ID
from create import path_to_folder, destination_folder, create_task_folder, start_update


bot = telebot.TeleBot('5820874061:AAGGpfqaRZkV7ZRHrezJEq41fdIeJ85KeUk')

form_data = {}



@bot.message_handler(commands=['start'])
def start(message):

    global values, keyboard

    values = get_task(file_zapusk)

    # Отображаем значок загрузки
    bot.send_chat_action(message.chat.id, 'typing')
    messagetoedit = bot.send_message(message.chat.id, 'Подождите...')

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
        bot.send_message(message.chat.id, "Ваш ID отсутствует в списке! Обратитесь к администратору.")
    else:
        bot.delete_message(message.chat.id, message_id=messagetoedit.message_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for adress in values.get(name):
            keyboard.add(telebot.types.InlineKeyboardButton(adress.split(', ')[-1], callback_data=name + ',' + str(values.get(name).index(adress))))
        # Отправка приветственного сообщения с инлайн-клавиатурой
        bot.send_message(message.chat.id, "Требуется предоставить АПО по объектам:", reply_markup=keyboard)


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
            form_data[user_id]['number'] = int(call.data.split(',')[1])
            form_data[user_id]['adr'] = values.get(form_data[user_id]['name'])[form_data[user_id]['number']]
            form_data[user_id]['филиал'] = form_data[user_id]['adr'].split(' ')[1]
            send_choice_message(call.message.chat.id)

        if call.data == "begin_apo":
            # Функция для отправки первого вопроса
            start_form(call.message)

        elif call.data == "load_photo":
            keyboard_folder = telebot.types.InlineKeyboardMarkup()
            keyboard_folder.row(telebot.types.InlineKeyboardButton("1 Схема замеров помещения", callback_data="1"))
            keyboard_folder.row(telebot.types.InlineKeyboardButton("2 Схема замеров фасада гл. вход", callback_data="2"))
            keyboard_folder.row(telebot.types.InlineKeyboardButton("3 Схема замеров фасада прав. стор.", callback_data="3"))
            keyboard_folder.row(telebot.types.InlineKeyboardButton("4 Схема замеров фасада левая стор.", callback_data="4"))
            keyboard_folder.row(telebot.types.InlineKeyboardButton("5 Схема размеров фасада обр. стор.", callback_data="5"))
            keyboard_folder.row(telebot.types.InlineKeyboardButton("6 Ситуационный план", callback_data="6"))
            keyboard_folder.row(telebot.types.InlineKeyboardButton("7 Конструктивная схема помещения", callback_data="7"))
            keyboard_folder.row(telebot.types.InlineKeyboardButton("8 Схема предварительного зонир.", callback_data="8"))
            keyboard_folder.add(telebot.types.InlineKeyboardButton("9 Схема кровли", callback_data="9"))
            keyboard_folder.add(telebot.types.InlineKeyboardButton("Назад", callback_data="back_to_main"))
            bot.send_message(call.message.chat.id, f"Выбран объект: {form_data[user_id]['adr']}. Выберите тип фото:", reply_markup=keyboard_folder)
   
        elif call.data == "back_to_main":
            bot.send_message(call.message.chat.id, f"Выберите действие по объекту: {form_data[user_id]['adr']}.", reply_markup=keyboard_2)

        elif call.data == "back":
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
            bot.send_message(call.message.chat.id, "Выберите тип фото:", reply_markup=keyboard_folder)
        elif call.data == 'No':

            # Если пользователь не будет больше подгружать фото 
            # Запуск макроса собирающего фото
            path_script = os.path.abspath(get_path_to_apo(call.message.chat.id)).replace("\\", "/")
            # Отображаем значок загрузки
            bot.send_chat_action(call.message.chat.id, 'typing')
            messagetoedit = bot.send_message(call.message.chat.id, 'Подождите...')

            run_vba_macro(path_script, 'module1', 'AddPhotosToSheet')

            # удаляем сообщение подождите...
            bot.delete_message(call.message.chat.id, message_id=messagetoedit.message_id)

            keyboard_approve = telebot.types.InlineKeyboardMarkup()
            keyboard_approve.add(telebot.types.InlineKeyboardButton("Согласовать", callback_data="approve"), telebot.types.InlineKeyboardButton("Пропустить", callback_data="not_approve"))
            bot.send_message(call.message.chat.id, "Для добавления подписи в документ нажмите Согласовать", reply_markup=keyboard_approve)
        
        elif call.data == 'approve':
            # Вставляем подпись
            file_name = os.path.abspath(get_path_to_apo(call.message.chat.id)).replace("\\", "/")
            print(file_name)
            run_vba_macro(file_name, 'module2', 'InsertImage')

            bot.send_message(call.message.chat.id, "Подпись добавлена!")
            
            # Конвертируем файл в ПДФ
            xlsm_to_pdf(file_name)
            # Находим путь к созданному ПДФ
            file_pdf = file_name.split(".xlsm")[0] + ".pdf"
            # Отправляем файл
            send_file_telegram(file_pdf, call.message.chat.id)

            bot.send_message(call.message.chat.id, "Требуется предоставить АПО по объектам:", reply_markup=keyboard)

        elif call.data == 'not_approve':
            file_name = get_path_to_apo(call.message.chat.id)
            send_file_telegram(file_name, call.message.chat.id)
            bot.send_message(call.message.chat.id, "Требуется предоставить АПО по объектам:", reply_markup=keyboard)

        if folder is not None:
            form_data[user_id]['objects_path'] = path_to_folder  + form_data[user_id]['adr'] + "\\Фото\\" + folder
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
    keyboard_foto.add(telebot.types.InlineKeyboardButton("Да", callback_data="Yes"), telebot.types.InlineKeyboardButton("Нет", callback_data="No"))
    bot.send_message(message.chat.id, "Хотите загрузить еще фото?", reply_markup=keyboard_foto)


# 1. Владелец 
def start_form(message):
    # form_data.clear()  # Очищаем данные формы перед началом
    # Добавляем филиал в словарь
    user_id = message.chat.id

    form_data[user_id]["адрес"] = ' '.join(form_data[user_id]["adr"].split(' ')[1:])
    # Находим полние имя РП
    for text in (RP_MSK + RP_SPB):
        if form_data[user_id]['name'] in text:
            form_data[user_id]["рп"] = text
    if form_data[user_id]['филиал'] == "МСК":
        form_data[user_id]["председатель"] = DF[0]
        form_data[user_id]["член_ком1"] = ROR[0]
    elif form_data[user_id]['филиал'] == "СПБ":
        form_data[user_id]["председатель"] = DF[1]
        form_data[user_id]["член_ком1"] = ROR[1]

    bot.send_message(
        message.chat.id,
        "Площадь помещения:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить"),
    )
    bot.register_next_step_handler(message, process_area)


# Функция для обработки ответа на вопрос о площади помещения
def process_area(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["площадь_помещения"] = "Пропущено"
        ask_floor(message)
        return
    form_data[message.chat.id]["площадь_помещения"] = message.text
    ask_floor(message)

# Функция для отправки вопроса об этаже
def ask_floor(message):
    bot.send_message(
        message.chat.id,
        "Расположено на этаже:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_floor)

# Функция для обработки ответа на вопрос об этаже
def process_floor(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["этаж"] = "Пропущено"
        ask_building_floors(message)
        return
    elif message.text == "Назад":
        if "этаж" in form_data:
            del form_data[message.chat.id]["этаж"]
        start_form(message)
        return
    form_data[message.chat.id]["этаж"] = message.text
    ask_building_floors(message)

# Функция для отправки вопроса о этажности здания
def ask_building_floors(message):
    bot.send_message(
        message.chat.id,
        "Этажность всего здания:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_building_floors)

# Функция для обработки ответа на вопрос о этажности здания
def process_building_floors(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["этажность"] = "Пропущено"
        askobjecttype(message)
        return
    elif message.text == "Назад":
        if "этажность" in form_data:
            del form_data[message.chat.id]["этажность"]
        ask_floor(message)
        return
    form_data[message.chat.id]["этажность"] = message.text
    askobjecttype(message)

# Функция для отправки вопроса о типе объекта
def askobjecttype(message): 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) 
    markup.add(types.KeyboardButton("Встроен./встроен.-пристроен.")) 
    markup.add(types.KeyboardButton("Торг. Центр")) 
    markup.add(types.KeyboardButton("Цоколь/подвал. Этаж")) 
    markup.add(types.KeyboardButton("Иные объекты")) 
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад")) 
    bot.send_message(message.chat.id, "12. Тип объекта:", reply_markup=markup) 
    bot.register_next_step_handler(message, processobjecttype)

 
def processobjecttype(message): 
    if message.text == "Пропустить": 
        form_data[message.chat.id]["тип_объекта"] = "Пропущено" 
        ask_basement_use_2(message) 
        return 
    elif message.text == "Назад": 
        if "тип_объекта" in form_data: 
            del form_data[message.chat.id]["тип_объекта"]
            ask_building_floors(message) 
        return 
    form_data[message.chat.id]["тип_объекта"] = message.text 
    ask_basement_use_2(message)


# Функция для отправки вопроса о помещении
def ask_basement_use_2(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Предполагается использование подвальных помещений:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_basement_use_2)

# Функция для обработки ответа на вопрос о использовании подвальных помещений
def process_basement_use_2(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["использование_подвала"] = "Пропущено"
        ask_comment_6(message)
        return
    elif message.text == "Назад":
        if "использование_подвала" in form_data:
            del form_data[message.chat.id]["использование_подвала"]
        askobjecttype(message)  # Укажите, какой вопрос требуется
        return
    form_data[message.chat.id]["использование_подвала"] = message.text
    ask_comment_6(message)

# Функция для отправки комментария
def ask_comment_6(message):
    bot.send_message(
        message.chat.id,
        "Комментарий:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_comment_6)


# Функция для обработки комментария
def process_comment_6(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["комментарий_6"] = "Пропущено"
        ask_plan_match(message)
        return
    elif message.text == "Назад":
        if "комментарий_6" in form_data:
            del form_data[message.chat.id]["комментарий_6"]
        ask_basement_use_2(message)
        return
    form_data[message.chat.id]["комментарий_6"] = message.text
    ask_plan_match(message)

# Функция для отправки вопроса о соответствии планировки
def ask_plan_match(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Фактическая планировка соответствует техпаспорту:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_plan_match)


# Функция для обработки ответа о соответствии планировки
def process_plan_match(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["соответствие_планировки"] = "Пропущено"
        ask_comment_7(message)
        return
    elif message.text == "Назад":
        if "соответствие_планировки" in form_data:
            del form_data[message.chat.id]["соответствие_планировки"]
        ask_comment_6(message)
        return
    form_data[message.chat.id]["соответствие_планировки"] = message.text
    ask_comment_7(message)


# Функция для отправки комментария
def ask_comment_7(message):
    bot.send_message(
        message.chat.id,
        "Комментарий:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_comment_7)


# Функция для обработки второго комментария
def process_comment_7(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["комментарий_7"] = "Пропущено"
        ask_foundation(message)
        return
    elif message.text == "Назад":
        if "комментарий_7" in form_data:
            del form_data[message.chat.id]["комментарий_7"]
        ask_plan_match(message)
        return
    form_data[message.chat.id]["комментарий_7"] = message.text
    ask_foundation(message)


# Функция для отправки вопроса о фундаменте
def ask_foundation(message):
    bot.send_message(
        message.chat.id,
        "Тип фундамента:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_foundation)


# Функция для обработки ответа о фундаменте
def process_foundation(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["фундамент"] = "Пропущено"
        ask_floors(message)
        return
    elif message.text == "Назад":
        if "фундамент" in form_data:
            del form_data[message.chat.id]["фундамент"]
        process_comment_7(message)
        return
    form_data[message.chat.id]["фундамент"] = message.text
    ask_floors(message)


# Функция для отправки вопроса о полах
def ask_floors(message):
    bot.send_message(
        message.chat.id,
        "Тип полов:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_floors)


# Функция для обработки ответа о полах
def process_floors(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["полы"] = "Пропущено"
        ask_load(message)
        return
    elif message.text == "Назад":
        if "полы" in form_data:
            del form_data[message.chat.id]["полы"]
        ask_foundation(message)
        return
    form_data[message.chat.id]["полы"] = message.text
    ask_load(message)


# Функция для отправки вопроса о расчетной нагрузке
def ask_load(message):
    bot.send_message(
        message.chat.id,
        "Расчетная нагрузка на квадратный метр:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_load)


# Функция для обработки ответа о расчетной нагрузке
def process_load(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["нагрузка"] = "Пропущено"
        ask_bearing_walls(message)
        return
    elif message.text == "Назад":
        if "нагрузка" in form_data:
            del form_data[message.chat.id]["нагрузка"]
        ask_floors(message)
        return
    form_data[message.chat.id]["нагрузка"] = message.text
    ask_bearing_walls(message)


# Функция для отправки вопроса о несущих стенах
def ask_bearing_walls(message):
    bot.send_message(
        message.chat.id,
        "Несущие стены:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_bearing_walls)


# Функция для обработки ответа о несущих стенах
def process_bearing_walls(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["стены"] = "Пропущено"
        ask_ceiling_type(message)
        return
    elif message.text == "Назад":
        if "стены" in form_data:
            del form_data[message.chat.id]["стены"]
        # Вернуться к предыдущему вопросу
        return
    form_data[message.chat.id]["стены"] = message.text
    ask_ceiling_type(message)


# Функция для отправки вопроса о типе перекрытия потолка
def ask_ceiling_type(message):
    bot.send_message(
        message.chat.id,
        "Тип перекрытия потолка:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_ceiling_type)


# Функция для обработки ответа о типе перекрытия потолка
def process_ceiling_type(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["тип_потолка"] = "Пропущено"
        ask_ceiling_material(message)
        return
    elif message.text == "Назад":
        if "тип_потолка" in form_data:
            del form_data[message.chat.id]["тип_потолка"]
        ask_bearing_walls(message)
        return
    form_data[message.chat.id]["тип_потолка"] = message.text
    ask_ceiling_material(message)


# Функция для отправки вопроса о материале перекрытия потолка
def ask_ceiling_material(message):
    bot.send_message(
        message.chat.id,
        "Материал перекрытия потолка:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_ceiling_material)


# Функция для обработки ответа о материале перекрытия потолка
def process_ceiling_material(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["материал_потолка"] = "Пропущено"
        ask_floor_type(message)
        return
    elif message.text == "Назад":
        if "материал_потолка" in form_data:
            del form_data[message.chat.id]["материал_потолка"]
        ask_ceiling_type(message)
        return
    form_data[message.chat.id]["материал_потолка"] = message.text
    ask_floor_type(message)


# Функция для отправки вопроса о типе перекрытия пола
def ask_floor_type(message):
    bot.send_message(
        message.chat.id,
        "Тип перекрытия пола:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_floor_type)


# Функция для обработки ответа о типе перекрытия пола
def process_floor_type(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["тип_пола"] = "Пропущено"
        ask_floor_material(message)
        return
    elif message.text == "Назад":
        if "тип_пола" in form_data:
            del form_data[message.chat.id]["тип_пола"]
        ask_ceiling_material(message)
        return
    form_data[message.chat.id]["тип_пола"] = message.text
    ask_floor_material(message)


# Функция для отправки вопроса о материале перекрытия пола
def ask_floor_material(message):
    bot.send_message(
        message.chat.id,
        "Материал перекрытия пола:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_floor_material)


# Функция для обработки ответа о материале перекрытия пола
def process_floor_material(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["материал_пола"] = "Пропущено"
        ask_roof_type(message)
        return
    elif message.text == "Назад":
        if "материал_пола" in form_data:
            del form_data[message.chat.id]["материал_пола"]
        ask_floor_type(message)
        return
    form_data[message.chat.id]["материал_пола"] = message.text
    ask_roof_type(message)


# Функция для отправки вопроса о типе кровли
def ask_roof_type(message):
    bot.send_message(
        message.chat.id,
        "Кровля:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_roof_type)


# Функция для обработки ответа о типе кровли
def process_roof_type(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["кровля"] = "Пропущено"
        ask_load_roof(message)
        return
    elif message.text == "Назад":
        if "кровля" in form_data:
            del form_data[message.chat.id]["кровля"]
        ask_floor_material(message)
        return
    form_data[message.chat.id]["кровля"] = message.text
    ask_load_roof(message)


# Функция для отправки вопроса о расчетной нагрузке кровли
def ask_load_roof(message):
    bot.send_message(
        message.chat.id,
        "Расчетная нагрузка на квадратный метр:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_load_roof)


# Функция для обработки ответа о расчетной нагрузке
def process_load_roof(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["нагрузка_кровли"] = "Пропущено"
        ask_structure_scheme(message)
        return
    elif message.text == "Назад":
        if "нагрузка" in form_data:
            del form_data[message.chat.id]["нагрузка_кровли"]
        ask_roof_type(message)
        return
    form_data[message.chat.id]["нагрузка_кровли"] = message.text
    ask_structure_scheme(message)


# Функция для отправки вопроса о конструктивной схеме здания
def ask_structure_scheme(message):
    bot.send_message(
        message.chat.id,
        "Конструктивная схема здания:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_structure_scheme)


# Функция для обработки ответа о конструктивной схеме здания
def process_structure_scheme(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["конструктивная_схема"] = "Пропущено"
        ask_defects(message)
        return
    elif message.text == "Назад":
        if "конструктивная_схема" in form_data:
            del form_data[message.chat.id]["конструктивная_схема"]
        ask_roof_type(message)
        return
    form_data[message.chat.id]["конструктивная_схема"] = message.text
    ask_defects(message)


# Функция для отправки вопроса о дефектах несущих конструкций
def ask_defects(message):
    bot.send_message(
        message.chat.id,
        "Дефекты несущих конструкций:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_defects)


# Функция для обработки ответа о дефектах несущих конструкций
def process_defects(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["дефекты"] = "Пропущено"
        ask_possibly(message)
        return
    elif message.text == "Назад":
        if "дефекты" in form_data:
            del form_data[message.chat.id]["дефекты"]
        ask_structure_scheme(message)
        return
    form_data[message.chat.id]["дефекты"] = message.text
    ask_possibly(message)


# Конец листа 3 ---------------------------------------------------------------


# Функция для отправки вопроса о требованиях по отклонению и уточнению
def ask_possibly(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Возможно"))
    markup.add(types.KeyboardButton("Невозможно"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "16. ВЫВОД: Использование помещений/здания в качестве магазина ТС «Монетка»:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_ask_possibly)


# Функция для обработки ответа о требованиях
def process_ask_possibly(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["возможность"] = "Пропущено"
        work_not_required(message)
        return
    elif message.text == "Назад":
        if "возможность" in form_data:
            del form_data[message.chat.id]["возможность"]
        ask_defects(message)
        return
    elif message.text == "Невозможно":
        form_data[message.chat.id]["возможность"] = message.text
        why_impossible(message)
        return
    form_data[message.chat.id]["возможность"] = message.text
    work_not_required(message)


# Функция для отправки вопроса о причинах невозможности
def why_impossible(message):
    bot.send_message(
        message.chat.id,
        "Укажите причину по которой использование помещений/здания в качестве магазина ТС «Монетка» невозможно:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_why_impossible)


# Функция для обработки ответа о о причинах невозможности
def process_why_impossible(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["причина_невозможности"] = "Пропущено"
        work_not_required(message)
        return
    elif message.text == "Назад":
        if "причина_невозможности" in form_data:
            del form_data[message.chat.id]["причина_невозможности"]
        ask_possibly(message)
        return
    form_data[message.chat.id]["причина_невозможности"] = message.text
    work_not_required(message)


 # Функция для отправки вопроса о требованиях по отклонению и уточнению
def work_not_required(message):
    bot.send_message(
        message.chat.id,
        "Работы, не требующие выполнения/замены (оставить существующие на объекте):",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_work_not_required)


# Работы, не требующие выполнения/замены
def process_work_not_required(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["работы_не_требующие"] = "Пропущено"
        ask_about_nonstandard_works(message)
        return
    elif message.text == "Назад":
        if "работы_не_требующие" in form_data:
            del form_data[message.chat.id]["работы_не_требующие"]
        ask_possibly(message)
        return
    form_data[message.chat.id]["работы_не_требующие"] = message.text
    ask_about_nonstandard_works(message)


# Нетиповые работы
def ask_about_nonstandard_works(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Есть ли необходимость в выполнении нетиповых работ?",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_ask_about_nonstandard_works)


def process_ask_about_nonstandard_works(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["нетиповые_работы"] = "Пропущено"
        ask_for_requirements_(message)
        return
    elif message.text == "Назад":
        if "нетиповые_работы" in form_data:
            del form_data[message.chat.id]["нетиповые_работы"]
        work_not_required(message)
        return
    elif message.text == "Нет":
        ask_for_requirements_(message)
        return
    elif message.text == "Да":
        ask_for_nonstandard_work_details(message)
        return


def ask_for_nonstandard_work_details(message):
    if "нетиповые_работы" not in form_data[message.chat.id]:
        form_data[message.chat.id]["нетиповые_работы"] = []
    ask_for_work_name(message)

def ask_for_work_name(message):
    bot.send_message(
        message.chat.id,
        "Введите наименование работ:",
    )
    bot.register_next_step_handler(message, process_work_name)


def process_work_name(message):
    work_name = message.text
    form_data[message.chat.id]["нетиповые_работы"].append({'тип_работ' : work_name})
    ask_for_work_deadline(message)


def ask_for_work_deadline(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("до АПП"))
    markup.add(types.KeyboardButton("до ВПК"))
    markup.add(types.KeyboardButton("Иной срок"))
    bot.send_message(
        message.chat.id,
        "Срок выполнения работ:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_work_deadline)


def process_work_deadline(message):
    deadline = message.text
    form_data[message.chat.id]["нетиповые_работы"][-1]["срок"] = deadline
    ask_for_work_responsible(message)


def process_work_deadline(message):
    deadline = message.text
    if deadline == "Иной срок":
        ask_for_custom_deadline(message)
        return
    form_data[message.chat.id]["нетиповые_работы"][-1]["срок"] = deadline
    ask_for_work_responsible(message)


def ask_for_custom_deadline(message):
    bot.send_message(
        message.chat.id,
        "Введите срок:",
    )
    bot.register_next_step_handler(message, process_custom_deadline)


def process_custom_deadline(message):
    custom_deadline = message.text
    form_data[message.chat.id]["нетиповые_работы"][-1]["срок"] = custom_deadline
    ask_for_work_responsible(message)


def ask_for_work_responsible(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("НОР"))
    markup.add(types.KeyboardButton("РП"))
    bot.send_message(
        message.chat.id,
        "Ответственный за выполнение:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_work_responsible)


def process_work_responsible(message):
    responsible = message.text
    form_data[message.chat.id]["нетиповые_работы"][-1]["ответственный"] = responsible
    ask_for_more_works(message)

def ask_for_more_works(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    bot.send_message(
        message.chat.id,
        "Нужно ли добавить еще работы?",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_more_works)


def process_more_works(message):
    if message.text == "Да":
        ask_for_nonstandard_work_details(message)
        return
    elif message.text == "Нет":
        ask_for_requirements_(message)
        return


def ask_for_requirements_(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Пропустить"))
    markup.add(types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Требования, утвержденные к выполнению применительно к данному объекту (дополнения, уточнения, отклонения от Стандарта):",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_requirements_)


def process_requirements_(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["требования_стандарт"] = "Пропущено"
        ask_for_construction_deadline(message)
        return
    elif message.text == "Назад":
        if "требования_стандарт" in form_data[message.chat.id]:
            del form_data[message.chat.id]["требования_стандарт"][-1]
        ask_for_more_works(message)
        return
    requirements = message.text
    form_data[message.chat.id]["требования_стандарт"] = requirements
    ask_for_construction_deadline(message)


def ask_for_construction_deadline(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Пропустить"))
    markup.add(types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Комиссией определен предварительный срок строительства:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_construction_deadline)


def process_construction_deadline(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["срок_строительства"] = "Пропущено"
        end_form(message)
        return
    elif message.text == "Назад":
        if "срок_строительства" in form_data[message.chat.id]:
            del form_data[message.chat.id]["срок_строительства"]
        ask_for_requirements_(message)
        return
    construction_deadline = message.text
    form_data[message.chat.id]["срок_строительства"] = construction_deadline
    end_form(message)


# Функция для завершения формы
def end_form(message):
    bot.send_message(message.chat.id, "Форма заполнена! Данные добавлены в АПО (при повторном заполнении АПО данные будут перезаписаны). Далее можно загрузить фото.")
    log_data_to_file(form_data[message.chat.id])

    file_name = get_path_to_apo(message.chat.id)
    print(file_name)
    insert_data_to_excel(file_name, form_data[message.chat.id])

    bot.send_message(message.chat.id, "ВАЖНО! Объект будет находиться в списке объектов по которым требуется АПО до тех пор пока в таблице запуск не будет снята отметка")
    send_choice_message(message.chat.id)


# Функция для создания клавиатуры с кнопками "Пропустить" и "Назад"
def create_keyboard_with_skip_and_back(skip_text, back_text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton(skip_text), types.KeyboardButton(back_text))
    return markup


def send_choice_message(chat_id):
    global keyboard_2
    keyboard_2 = telebot.types.InlineKeyboardMarkup()
    keyboard_2.row(
        telebot.types.InlineKeyboardButton("Заполнить АПО", callback_data="begin_apo"),
        telebot.types.InlineKeyboardButton("Загрузить фото", callback_data="load_photo"))
    keyboard_2.row(telebot.types.InlineKeyboardButton("Назад", callback_data="back"))
    bot.send_message(chat_id, f"Выберите действие по объекту: {form_data[chat_id]['adr']}.", reply_markup=keyboard_2)


def get_path_to_apo(chat_id):
    adress = values.get(form_data[chat_id]['name'])[form_data[chat_id]['number']]
    name_apo = ' '.join(adress.split(' ')[1:])
    path_to_file = '../АПО/' + '/' + adress + '/АПО ' + name_apo + '.xlsm'
    return path_to_file


def send_file_telegram(file_path, chat_id):

    # Проверка существования файла
    if not os.path.exists(file_path):
        print("Файл не найден:", file_path)
        return False

    # Отправка файла
    try:
        with open(file_path, 'rb') as file:
            bot.send_document(chat_id=chat_id, document=file)
        print("Файл успешно отправлен.")
        return True
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")
        return False


# bot.polling(none_stop=True)

while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        if time.gmtime().tm_min in (0, 10, 20, 30, 40, 50) and time.gmtime().tm_sec < 31:
            start_update(path_to_folder, destination_folder)
        print(e)
        time.sleep(15)
