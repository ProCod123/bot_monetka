import telebot
from telebot import types
import os
import time


from log_data import log_data_to_file
from work_with_exel import get_task, get_name, file_zapusk, run_vba_macro
from export import insert_data_to_excel
from workers import DF, ROR, RP_MSK, RP_SPB

bot = telebot.TeleBot('5209749192:AAEyxtpL5ndVu8-cs77LgG_W878lqKGaT-I')



form_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    global values
    
    # Отображаем значок загрузки
    bot.send_chat_action(message.chat.id, 'typing')

    values = get_task(file_zapusk)
    global keyboard

    name = get_name(message.chat.id)
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
            bot.send_message(call.message.chat.id, "Требуется предоставить АПО по объектам:", reply_markup=keyboard)

        if folder is not None:
            form_data[user_id]['objects_path'] = os.path.abspath("..\\" + os.curdir) + "\Объекты" + '\\' + form_data[user_id]['adr'] + "\\Акты\\АПО\\Фото\\" + folder
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

    # Запуск макроса собирающего фото
    path_script = os.path.abspath(get_path_to_apo(message.chat.id)).replace("\\", "/")
    run_vba_macro(path_script, 'module1', 'DeletePhoto')
    run_vba_macro(path_script, 'module1', 'AddPhotosToSheet')


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
        "1. Владелец объекта:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_owner)


# Функция для обработки ответа на вопрос о владельце
def process_owner(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["владелец"] = "Пропущено"
        ask_owner_information(message)
        return
    elif message.text == "Назад":
        if "владелец" in form_data:
            del form_data[message.chat.id]["владелец"]
        start_form(message)
        return
    form_data[message.chat.id]["владелец"] = message.text
    ask_owner_information(message)


# Контакты владельца
def ask_owner_information(message):
    bot.send_message(
        message.chat.id,
        "Контакты владельца:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_owner_information)

# Контакты владельца
def process_owner_information(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["контакты_владельца"] = "Пропущено"
        ask_user(message)
        return
    elif message.text == "Назад":
        if "контакты_владельца" in form_data:
            del form_data[message.chat.id]["контакты_владельца"]
        start_form(message)
        return
    form_data[message.chat.id]["контакты_владельца"] = message.text
    ask_user(message)


# 2.  о пользователе/арендаторе
def ask_user(message):
    bot.send_message(
        message.chat.id,
        "2. Пользователь, арендатор объекта:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_user)

# 2. пользователе/арендаторе
def process_user(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["пользователь"] = "Пропущено"
        ask_user_info(message)
        return
    elif message.text == "Назад":
        if "пользователь" in form_data:
            del form_data[message.chat.id]["пользователь"]
        ask_owner_information(message)
        return
    form_data[message.chat.id]["пользователь"] = message.text
    ask_user_info(message)


# Контакты пользователя
def ask_user_info(message):
    bot.send_message(
        message.chat.id,
        "Контакты пользователя, арендатора объекта:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_user_info)

# Обработка контактов
def process_user_info(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["контакты_пользователя"] = "Пропущено"
        ask_function(message)
        return
    elif message.text == "Назад":
        if "пользователь" in form_data:
            del form_data[message.chat.id]["контакты_пользователя"]
        ask_user(message)
        return
    form_data[message.chat.id]["контакты_пользователя"] = message.text
    ask_function(message)


# Функция для отправки вопроса о функциональном назначении здания
def ask_function(message):
    bot.send_message(
        message.chat.id,
        "3. Функциональное назначение здания по документам:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_function)

# Функция для обработки ответа на вопрос о функциональном назначении здания
def process_function(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["функциональное_назначение"] = "Пропущено"
        ask_ownership_type(message)
        return
    elif message.text == "Назад":
        if "функциональное_назначение" in form_data:
            del form_data[message.chat.id]["функциональное_назначение"]
        ask_user(message)
        return
    form_data[message.chat.id]["функциональное_назначение"] = message.text
    ask_ownership_type(message)

# Функция для отправки вопроса о праве владения
def ask_ownership_type(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Аренда"))
    markup.add(types.KeyboardButton("Аренды (будущей вещи)"))
    markup.add(types.KeyboardButton("Купли-продажи"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id, "4. Право владения объектом, планируется по Договору:", reply_markup=markup
    )
    bot.register_next_step_handler(message, process_ownership_type)

# Функция для обработки ответа на вопрос о праве владения
def process_ownership_type(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["право_владения"] = "Пропущено"
        ask_comments(message)
        return
    elif message.text == "Назад":
        if "право_владения" in form_data:
            del form_data[message.chat.id]["право_владения"]
        ask_function(message)
        return
    form_data[message.chat.id]["право_владения"] = message.text
    ask_comments(message)

# Функция для отправки вопроса о комментариях
def ask_comments(message):
    bot.send_message(
        message.chat.id,
        "Комментарии:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_comments)

# Функция для обработки ответа на вопрос о комментариях
def process_comments(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["комментарии_1"] = "Пропущено"
        ask_property_status(message)
        return
    elif message.text == "Назад":
        if "комментарии" in form_data:
            del form_data[message.chat.id]["комментарии_1"]
        ask_ownership_type(message)
        return
    form_data[message.chat.id]["комментарии_1"] = message.text
    ask_property_status(message)

# Функция для отправки вопроса о статусе собственности
def ask_property_status(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Частная собственность"))
    markup.add(types.KeyboardButton("Муниципальная собственность"))
    markup.add(types.KeyboardButton("Государственная собственность"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id, "5. Планируемый объект является:", reply_markup=markup
    )
    bot.register_next_step_handler(message, process_property_status)

# Функция для обработки ответа на вопрос о статусе собственности
def process_property_status(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["собственность"] = "Пропущено"
        ask_comments_2(message)
        return
    elif message.text == "Назад":
        if "собственность" in form_data:
            del form_data[message.chat.id]["собственность"]
        ask_comments(message)
        return
    form_data[message.chat.id]["собственность"] = message.text
    ask_comments_2(message)

# Функция для отправки вопроса о комментариях
def ask_comments_2(message):
    bot.send_message(
        message.chat.id,
        "Комментарии:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_comments_2)

# Функция для обработки ответа на вопрос о комментариях
def process_comments_2(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["комментарии_2"] = "Пропущено"
        ask_building_monument(message)
        return
    elif message.text == "Назад":
        if "комментарии_2" in form_data:
            del form_data[message.chat.id]["комментарии_2"]
        ask_property_status(message)
        return
    form_data[message.chat.id]["комментарии_2"] = message.text
    ask_building_monument(message)


# Функция для отправки вопроса о статусе здания (памятник архитектуры)
def ask_building_monument(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "6. Здание, в котором расположен планируемый объект, по документам является памятником архитектуры:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_building_monument)

# Функция для обработки ответа на вопрос о статусе здания (памятник архитектуры)
def process_building_monument(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["памятник"] = "Пропущено"
        ask_building_commissioned(message)
        return
    elif message.text == "Назад":
        if "памятник" in form_data:
            del form_data[message.chat.id]["памятник"]
        ask_property_status(message)
        return
    form_data[message.chat.id]["памятник"] = message.text
    ask_building_commissioned(message)


# Функция для отправки вопроса о статусе здания (введено в эксплуатацию)
def ask_building_commissioned(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Здание по документам введено в эксплуатацию:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_building_commissioned)

# Функция для обработки ответа на вопрос о статусе здания (введено в эксплуатацию)
def process_building_commissioned(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["эксплуатация"] = "Пропущено"
        ask_building_condition(message)
        return
    elif message.text == "Назад":
        if "эксплуатация" in form_data:
            del form_data[message.chat.id]["эксплуатация"]
        ask_building_monument(message)
        return
    form_data[message.chat.id]["эксплуатация"] = message.text
    ask_building_condition(message)

# Функция для отправки вопроса о состоянии здания (ветхость/аварийность)
def ask_building_condition(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Здание по документам признано ветхим/аварийным:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_building_condition)

# Функция для обработки ответа на вопрос о состоянии здания (ветхость/аварийность)
def process_building_condition(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["ветхость"] = "Пропущено"
        ask_room_basement(message)
        return
    elif message.text == "Назад":
        if "ветхость" in form_data:
            del form_data[message.chat.id]["ветхость"]
        ask_building_commissioned(message)
        return
    form_data[message.chat.id]["ветхость"] = message.text
    ask_comments_3(message)


# Функция для отправки вопроса о комментариях
def ask_comments_3(message):
    bot.send_message(
        message.chat.id,
        "Комментарии:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_comments_3)

# Функция для обработки ответа на вопрос о комментариях
def process_comments_3(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["комментарии_3"] = "Пропущено"
        ask_room_basement(message)
        return
    elif message.text == "Назад":
        if "комментарии_3" in form_data:
            del form_data[message.chat.id]["комментарии_3"]
        ask_building_condition(message)
        return
    form_data[message.chat.id]["комментарии_3"] = message.text
    ask_room_basement(message)



# Функция для отправки вопроса о статусе помещения (цокольный этаж)
def ask_room_basement(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "7. Планируемое помещение (объект), по документам является цокольным этажом:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_room_basement)

# Функция для обработки ответа на вопрос о статусе помещения (цокольный этаж)
def process_room_basement(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["цоколь"] = "Пропущено"
        ask_one_owner(message)
        return
    elif message.text == "Назад":
        if "цоколь" in form_data:
            del form_data[message.chat.id]["цоколь"]
        ask_building_condition(message)
        return
    form_data[message.chat.id]["цоколь"] = message.text
    ask_one_owner(message)

# Функция для отправки вопроса о статусе собственности
def ask_one_owner(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Объект принадлежит одному собственнику:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_one_owner)

# Функция для обработки ответа на вопрос о статусе собственности
def process_one_owner(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["один_собственник"] = "Пропущено"
        ask_comments_4(message)
        return
    elif message.text == "Назад":
        if "один_собственник" in form_data:
            del form_data[message.chat.id]["один_собственник"]
        ask_room_basement(message)
        return
    form_data[message.chat.id]["один_собственник"] = message.text
    ask_comments_4(message)


# Функция для отправки вопроса о комментариях
def ask_comments_4(message):
    bot.send_message(
        message.chat.id,
        "Комментарии:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_comments_4)

# Функция для обработки ответа на вопрос о комментариях
def process_comments_4(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["комментарии_4"] = "Пропущено"
        ask_basement_use_1(message)
        return
    elif message.text == "Назад":
        if "комментарии_4" in form_data:
            del form_data[message.chat.id]["комментарии_4"]
        ask_one_owner(message)
        return
    form_data[message.chat.id]["комментарии_4"] = message.text
    ask_basement_use_1(message)


# 15 Функция для отправки вопроса об использовании подвальных помещений
def ask_basement_use_1(message):
    bot.send_message(
        message.chat.id,
        "8. Планируется использование подвальных помещений (если да, под какие цели (подсобки, ЦХМ и т.д.)):",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_basement_use_1)


#  Функция для обработки ответа на вопрос об использовании подвальных помещений
def process_basement_use_1(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["подвальные_помещения"] = "Пропущено"
        ask_basement_document(message)
        return
    elif message.text == "Назад":
        if "подвальные_помещения" in form_data:
            del form_data[message.chat.id]["подвальные_помещения"]
        ask_comments_4(message)
        return
    form_data[message.chat.id]["подвальные_помещения"] = message.text
    ask_basement_document(message)


# Функция для отправки вопроса о оформлении подвальных помещений
def ask_basement_document(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Все помещения"))
    markup.add(types.KeyboardButton("Не все помещения"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "В случае использования подвальных помещений по Договору аренды будут оформлены:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_basement_document)


# Функция для обработки ответа на вопрос о оформлении подвальных помещений
def process_basement_document(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["документы_подвала"] = "Пропущено"
        ask_comments_5(message)
        return
    elif message.text == "Назад":
        if "документы_подвала" in form_data:
            del form_data[message.chat.id]["документы_подвала"]
        ask_basement_use_1(message)
        return
    form_data[message.chat.id]["документы_подвала"] = message.text
    ask_comments_5(message)

# Функция для отправки вопроса о комментариях
def ask_comments_5(message):
    bot.send_message(
        message.chat.id,
        "Комментарии:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_comments_5)

# Функция для обработки ответа на вопрос о комментариях
def process_comments_5(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["комментарии_5"] = "Пропущено"
        ask_traffic(message)
        return
    elif message.text == "Назад":
        if "комментарии_5" in form_data:
            del form_dat[message.chat.id]["комментарии_5"]
        ask_basement_document(message)
        return
    form_data[message.chat.id]["комментарии_5"] = message.text
    ask_traffic(message)



# Функция для отправки вопроса об ориентированности
def ask_traffic(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Пешеходный трафик"))
    markup.add(types.KeyboardButton("Автомобильный трафик"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id, "9. Основная ориентированность на:", reply_markup=markup
    )
    bot.register_next_step_handler(message, process_traffic)

# Функция для обработки ответа на вопрос об ориентированности
def process_traffic(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["трафик"] = "Пропущено"
        ask_area(message)
        return
    elif message.text == "Назад":
        if "трафик" in form_data:
            del form_data[message.chat.id]["трафик"]
        ask_comments_5(message)
        return
    form_data[message.chat.id]["трафик"] = message.text
    ask_area(message)

# Начало листа 3 -----------------------------------------


# Функция для отправки вопроса о площади помещения
def ask_area(message):
    bot.send_message(
        message.chat.id,
        "9. Площадь помещения, планируемая в аренду/покупку:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_area)

# Функция для обработки ответа на вопрос о площади помещения
def process_area(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["площадь_помещения"] = "Пропущено"
        ask_floor(message)
        return
    elif message.text == "Назад":
        if "площадь_помещения" in form_data:
            del form_data[message.chat.id]["площадь_помещения"]
        ask_traffic(message)
        return
    form_data[message.chat.id]["площадь_помещения"] = message.text
    ask_floor(message)

# Функция для отправки вопроса об этаже
def ask_floor(message):
    bot.send_message(
        message.chat.id,
        "10. Расположено на этаже:",
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
        ask_area(message)
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
    bot.send_message(message.chat.id, "11. Тип объекта:", reply_markup=markup) 
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
        "11. Предполагается использование подвальных помещений:",
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
        ask_basement_use(message)
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
        "12. Фактическая планировка соответствует техпаспорту:",
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
        "13. Тип фундамента:",
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
        ask_opening_in_wall(message)
        return
    elif message.text == "Назад":
        if "дефекты" in form_data:
            del form_data[message.chat.id]["дефекты"]
        ask_structure_scheme(message)
        return
    form_data[message.chat.id]["дефекты"] = message.text
    ask_opening_in_wall(message)

# Функция для отправки вопроса о необходимости устройства проема в несущей стене
def ask_opening_in_wall(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "14. На планируемом объекте потребуется устройство проема в несущей стене:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_opening_in_wall)

# Функция для обработки ответа о необходимости устройства проема в несущей стене
def process_opening_in_wall(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["проем"] = "Пропущено"
        ask_replacement_elements(message)
        return
    elif message.text == "Назад":
        if "проем" in form_data:
            del form_data[message.chat.id]["проем"]
        ask_defects(message)
        return
    form_data[message.chat.id]["проем"] = message.text
    ask_replacement_elements(message)

# Функция для отправки вопроса о необходимости замены или установки элементов несущих конструкций
def ask_replacement_elements(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Потребуется замена или дополнительная установка элементов несущих конструкций:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_replacement_elements)

# Функция для обработки ответа о необходимости замены или установки элементов несущих конструкций
def process_replacement_elements(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["замена_элементов"] = "Пропущено"
        ask_reconstruction_area(message)
        return
    elif message.text == "Назад":
        if "замена_элементов" in form_data:
            del form_data[message.chat.id]["замена_элементов"]
        ask_opening_in_wall(message)
        return
    form_data[message.chat.id]["замена_элементов"] = message.text
    ask_reconstruction_area(message)

# Функция для отправки вопроса о площади планируемой реконструкции
def ask_reconstruction_area(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "Площадь планируемой реконструкции более 1500м2:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_reconstruction_area)

# Функция для обработки ответа о площади планируемой реконструкции
def process_reconstruction_area(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["площадь_реконструкции"] = "Пропущено"
        ask_extension(message)
        return
    elif message.text == "Назад":
        if "площадь_реконструкции" in form_data:
            del form_data[message.chat.id]["площадь_реконструкции"]
        ask_replacement_elements(message)
        return
    form_data[message.chat.id]["площадь_реконструкции"] = message.text
    ask_extension(message)

# Функция для создания клавиатуры с вариантами Да, Нет, Пропустить, Назад
def create_yes_no_skip_back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
    markup.row(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    return markup


# Функция для отправки вопроса о строительстве теплого пристроя
def ask_extension(message):
    bot.send_message(
        message.chat.id,
        "Будет ли при переустройстве помещения увеличение объема здания за счет строительства теплого пристроя?",
        reply_markup=create_yes_no_skip_back_keyboard(),
    )
    bot.register_next_step_handler(message, process_extension)

# Функция для обработки ответа о строительстве теплого пристроя
def process_extension(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["пристройка"] = "Пропущено"
        ask_ceiling_height(message)
        return
    elif message.text == "Назад":
        if "пристройка" in form_data:
            del form_data[message.chat.id]["пристройка"]
        ask_reconstruction_area(message)
        return
    form_data[message.chat.id]["пристройка"] = message.text
    ask_ceiling_height(message)

# Функция для отправки вопроса о увеличении высоты потолков
def ask_ceiling_height(message):
    bot.send_message(
        message.chat.id,
        "Увеличение объема здания за счет увеличения высоты потолков за счет выемки грунта, переустройства полов",
        reply_markup=create_yes_no_skip_back_keyboard(),
    )
    bot.register_next_step_handler(message, process_ceiling_height)

# Функция для обработки ответа о увеличении высоты потолков
def process_ceiling_height(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["потолки"] = "Пропущено"
        ask_roof_reconstruction(message)
        return
    elif message.text == "Назад":
        if "потолки" in form_data:
            del form_data[message.chat.id]["потолки"]
        ask_extension(message)
        return
    form_data[message.chat.id]["потолки"] = message.text
    ask_roof_reconstruction(message)


# Функция для отправки вопроса о переустройстве кровли
def ask_roof_reconstruction(message):
    bot.send_message(
        message.chat.id,
        "Увеличение объема здания за счет переустройства кровли?",
        reply_markup=create_yes_no_skip_back_keyboard(),
    )
    bot.register_next_step_handler(message, process_roof_reconstruction)

# Функция для обработки ответа о переустройстве кровли
def process_roof_reconstruction(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["кровля_переустройство"] = "Пропущено"
        ask_construction_definition(message)
        return
    elif message.text == "Назад":
        if "кровля_переустройство" in form_data:
            del form_data[message.chat.id]["кровля_переустройство"]
        ask_ceiling_height(message)
        return
    form_data[message.chat.id]["кровля_переустройство"] = message.text
    ask_construction_definition(message)


# Функция для отправки вопроса о типе строительства
def ask_construction_definition(message):
    bot.send_message(
        message.chat.id,
        "Объект попадает под официальное определение типа строительства:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_construction_definition)

# Функция для обработки ответа о типе строительства
def process_construction_definition(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["тип_строительства"] = "Пропущено"
        ask_expertise(message)
        return
    elif message.text == "Назад":
        if "тип_строительства" in form_data:
            del form_data[message.chat.id]["тип_строительства"]
        ask_construction_definition(message)
        return
    form_data[message.chat.id]["тип_строительства"] = message.text
    ask_expertise(message)

# Функция для отправки вопроса о прохождении экспертизы проектной документации
def ask_expertise(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Да"))
    markup.add(types.KeyboardButton("Нет"))
    markup.add(types.KeyboardButton("Пропустить"), types.KeyboardButton("Назад"))
    bot.send_message(
        message.chat.id,
        "15. Прохождение экспертизы проектной документации:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_expertise)

# Функция для обработки ответа о прохождении экспертизы проектной документации
def process_expertise(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["экспертиза"] = "Пропущено"
        ask_requirements(message)
        return
    elif message.text == "Назад":
        if "экспертиза" in form_data:
            del form_data[message.chat.id]["экспертиза"]
        ask_construction_definition(message)
        return
    form_data[message.chat.id]["экспертиза"] = message.text
    ask_requirements(message)

# Функция для отправки вопроса о требованиях по отклонению и уточнению
def ask_requirements(message):
    bot.send_message(
        message.chat.id,
        "16. Предложение для рассмотрения комиссией требований по отклонению, дополнению, уточнению к действующему стандарту на строительство и оснащение магазинов ТС Монетка, применительно к данному объекту:",
        reply_markup=create_keyboard_with_skip_and_back("Пропустить", "Назад"),
    )
    bot.register_next_step_handler(message, process_requirements)

# Функция для обработки ответа о требованиях
def process_requirements(message):
    if message.text == "Пропустить":
        form_data[message.chat.id]["требования"] = "Пропущено"
        end_form(message)
        return
    elif message.text == "Назад":
        if "требования" in form_data:
            del form_data[message.chat.id]["требования"]
        ask_expertise(message)
        return
    form_data[message.chat.id]["требования"] = message.text
    end_form(message)

# Конец листа 3 ---------------------------------------------------------------


# Функция для завершения формы
def end_form(message):
    bot.send_message(message.chat.id, "Форма заполнена! Данные добавлены в АПО")
    log_data_to_file(form_data[message.chat.id])

    file_name = get_path_to_apo(message.chat.id)
    insert_data_to_excel(file_name, form_data[message.chat.id])

    # filled = ''

    # for key, value in form_data[message.chat.id].items():
    #     filled += f"{key}: {value} \n"
    # bot.send_message(message.chat.id, filled)
    send_file_telegram(file_name, message.chat.id)

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
    path_to_file = '../Объекты/' + adress + '/Акты/АПО/АПО ' + name_apo + '.xlsm'

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

bot.polling(none_stop=True)

# while True:
#     try:
#         bot.polling(none_stop=True)

#     except Exception as e:
#         print(e)
#         time.sleep(15)


