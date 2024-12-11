import re




text = """
def start_form(message):
    # form_data.clear()  # Очищаем данные формы перед началом
    # Добавляем филиал в словарь
    user_id = message.chat.id
    update_form_data(user_id, data)["адрес"] = ' '.join(update_form_data(user_id, data)["adr"].split(' ')[1:])
    # Находим полние имя РП
    for text in (RP_MSK + RP_SPB):
        if update_form_data(user_id, data)['name'] in text:
            update_form_data(user_id, data)["рп"] = text
    if update_form_data(user_id, data)['филиал'] == "МСК":
        update_form_data(user_id, data)["председатель"] = DF[0]
        update_form_data(user_id, data)["член_ком1"] = ROR[0]
    elif update_form_data(user_id, data)['филиал'] == "СПБ":
        update_form_data(user_id, data)["председатель"] = DF[1]
        update_form_data(user_id, data)["член_ком1"] = ROR[1]

    """
# new = text.replace('form_data[user_id]', 'update_form_data(user_id, data)')
# print(new)
