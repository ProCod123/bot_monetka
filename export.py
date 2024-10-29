
import openpyxl
from workers import ROR


def insert_data_to_excel(file_name, data_dict):
    try:
        workbook = openpyxl.load_workbook(file_name, keep_vba=True)
    except FileNotFoundError:
        workbook = openpyxl.Workbook()

    for sheet_name in ('1', '2', '3', '4 гор', '5-8 гор', '9-10', '11'):
        worksheet = workbook[sheet_name] # Получение листа

        # Соответствие ключей словаря ячейкам
        cell_mapping = {}

        if sheet_name == '1':
            mark = ()
            cell_mapping = {
                "председатель": "B15",
                "член_ком1": "B20",
                "рп": "B22",
            }
        elif sheet_name == '2':
            if data_dict.get("филиал") == "МСК":
                worksheet["C38"] = ROR[0]
            else:
                worksheet["C38"] = ROR[1]
            
            mark = (
                    'E15', 'E16', 'E17', 'E19', 'E20', 'E21', 'F23', 'H23', 'E20', 'F24','H24', 'F25', 'H25', 'F27', 'H27',
                    'F28', 'H28', 'E33', 'J33', 'E35', 'J35'
                    )
            
            # Очищаем ранее заполненные данные
            for cell in mark:
                worksheet[cell] = ''

            # 5. Право владения объектом, планируется  по Договору:
            if data_dict.get("право_владения") == "Аренда":
                pravo = "E15"
            elif data_dict.get("право_владения") == "Аренды (будущей вещи)":
                pravo = "E16"
            else:
                pravo = "E17"

            # 6. Планируемый объект является:
            if data_dict.get("собственность") == "Частная собственность":
                own = "E19"
            elif data_dict.get("собственность") == "Муниципальная собственность":
                own = "E20"
            else:
                own = "E21"

            # является памятником архитектуры
            if data_dict.get("памятник") == "Да":
                memorial = "F23"
            else:
                memorial = "H23"

            # Введено в эксплуатацию
            if data_dict.get("эксплуатация") == "Да":
                exploitation = "F24"
            else:
                exploitation = "H24"

            # признано ветхим/аварийным
            if data_dict.get("ветхость") == "Да":
                dilapidation = "F25"
            else:
                dilapidation = "H25"

            # цоколь
            if data_dict.get("цоколь") == "Да":
                base = "F27"
            else:
                base = "H27"    

            # один_собственник    
            if data_dict.get("один_собственник") == "Да":
                one_owner = "F28"
            else:
                one_owner = "H28"

            # Договору аренды будут оформлены  
            if data_dict.get("документы_подвала") == "Все помещения":
                basment_doc = "E33"
            else:
                basment_doc = "J33"

            # Основная ориентированность на   
            if data_dict.get("трафик") == "Пешеходный трафик":
                traffic = "E35"
            else:
                traffic = "J35"

            cell_mapping = {
                "адрес": "B6",
                "владелец": "B7",
                "контакты_владельца": "B8",
                "пользователь": "B10",
                "контакты_пользователя": "B11",
                "функциональное_назначение": "C13",
                "право_владения": pravo,
                "комментарии_1": "B18",
                "собственность": own,
                "комментарии_2": "B22",
                "памятник": memorial,
                "эксплуатация": exploitation,
                "ветхость": dilapidation,
                "комментарии_3": "B26",
                "цоколь": base,
                "один_собственник": one_owner,
                "комментарии_4": "B29",
                "подвальные_помещения": "C30",
                "документы_подвала": basment_doc,
                "комментарии_5": "B34",
                "трафик": traffic,
            }

        elif sheet_name == '3':
            worksheet["C59"] = data_dict.get("рп")

            # тип объекта:
            if data_dict.get("тип_объекта") == "Встроен./встроен.-пристроен.":
                tipe_of_object = "E7"
            elif data_dict.get("тип_объекта") == "Торг. Центр":
                tipe_of_object = "E8"
            elif data_dict.get("тип_объекта") == "Цоколь/подвал. Этаж":
                tipe_of_object = "E9"
            else:
                tipe_of_object = "E10"


            if data_dict.get("использование_подвала") == "Да":
                using_base = "H12"
            else:
                using_base = "J12"

            if data_dict.get("соответствие_планировки") == "Да":
                compliance = "E15"
            else:
                compliance = "G15"

            if data_dict.get("проем") == "Да":
                door = "E32"
            else:
                door = "J32"

            if data_dict.get("замена_элементов") == "Да":
                change_element = "E33"
            else:
                change_element = "J33"

            if data_dict.get("площадь_реконструкции") == "Да":
                square = "E35"
            else:
                square = "J35"

            if data_dict.get("пристройка") == "Да":
                extension = "E39"
            else:
                extension = "J39"

            if data_dict.get("потолки") == "Да":
                ceilings = "E40"
            else:
                ceilings = "J40"

            if data_dict.get("кровля_переустройство") == "Да":
                roof_reconstruction = "E42"
            else:
                roof_reconstruction = "J42"

            if data_dict.get("экспертиза") == "Да":
                expertise = "E49"
            else:
                expertise = "J49"

            mark = ("E7", "E8", "E9", "E10", "H12", "J12", "E15", "G15", "E32", "J32", "E33", 
                    "J33", "E35", "J35", "E39", "J39", "E40", "J40", "E42", "J42", "E49", "J49")

            # Очищаем ранее заполненные данные
            for cell in mark:
                worksheet[cell] = ''

            cell_mapping = {
                "площадь_помещенияь": "C4",
                "этаж": "B5",
                "этажность": "E5",
                "тип_объекта": tipe_of_object,
                "использование_подвала": using_base,
                "комментарий_6": "B13",
                "соответствие_планировки": compliance,
                "комментарий_7": "B16",
                "фундамент": "B20",
                "полы": "B21",
                "нагрузка": "E21",
                "стены": "B22",
                "тип_потолка": "C23",
                "материал_потолка": "H23",
                "тип_пола": "C24",
                "материал_пола": "H24",
                "кровля": "B25",
                "нагрузка_кровли": "E25",
                "конструктивная_схема": "C27",
                "дефекты": "C28",

                "проем": door,
                "замена_элементов": change_element,
                "площадь_реконструкции": square,
                "пристройка": extension,
                "потолки": ceilings,
                "кровля_переустройство": roof_reconstruction,

                "тип_строительства": "D45",
                "экспертиза": expertise,
                "требования": "A52",

            }


        elif sheet_name == '4 гор':
            worksheet['B34'] = data_dict.get('рп')

        elif sheet_name == '5-8 гор':
            worksheet['B37'] = data_dict.get('рп')
            worksheet['B70'] = data_dict.get('рп')
            worksheet['B108'] = data_dict.get('рп')

        elif sheet_name == '9-10':
            worksheet['B22'] = data_dict.get('рп')
            worksheet['B24'] = data_dict.get('член_ком1')
            worksheet['B108'] = data_dict.get('председатель')
            worksheet['B58'] = data_dict.get('рп')

        elif sheet_name == '11':
            worksheet['A12'] = data_dict.get('')
            worksheet['B47'] = data_dict.get('рп')
            worksheet['B44'] = data_dict.get('председатель')
            mark = (
                    'B6', 'B10',
                    )
            
            # Очищаем ранее заполненные данные
            for cell in mark:
                worksheet[cell] = ''

            for row in range(21, 34):
                for col in (1, 2, 3, 4, 5, 9):
                    worksheet.cell(row=row, column=col).value = ''   

            # ВЫВОД: Использование помещений/здания в качестве магазина ТС «Монетка»:
            if data_dict.get("возможность") == "Возможно":
                possibly = "B6"
            else:
                possibly = "B10"

            cell_mapping = {
                "возможность" : possibly,
                "причина_невозможности": "A12",
                "работы_не_требующие": "A15",
                "требования" : "A37",
                "срок_строительства" : "D41"
            }
            # Заполняем таблицу
            if "нетиповые_работы" in data_dict:
                if data_dict.get("нетиповые_работы") != "Пропущено":
                    for i, item in enumerate(data_dict.get("нетиповые_работы")):
                        worksheet['A' + str(21 + i)] = i + 1
                        worksheet['B' + str(21 + i)] = item.get("тип_работ")
                        if item.get("срок") == "до АПП":
                            worksheet['C' + str(21 + i)] = "X"
                        elif item.get("срок") == "до ВПК":
                            worksheet['D' + str(21 + i)] = "X"
                        else:
                            worksheet['E' + str(21 + i)] = "X"
                        worksheet['I' + str(21 + i)] = item.get("ответственный")
    

        # Запись данных в ячейки
        for key, value in data_dict.items():
            if key in cell_mapping.keys():
                cell = cell_mapping[key]
                if value == 'Пропущено':
                    pass
                else:
                    if cell in mark:
                        worksheet[cell] = 'X'
                    else:
                        worksheet[cell] = value

    workbook.save(file_name) # Сохранение изменений
    print(f"Данные успешно вставлены в файл '{file_name}'.")


# file = '../Объекты/2 СПБ ЛО, г.п. Ульяновка Калинина, д. 1/Акты/АПО/АПО СПБ ЛО, г.п. Ульяновка Калинина, д. 1.xlsm'
# data = {'id': 1644147255, 'филиал': 'МСК', 'адрес': 'МСК МО, Первомайское Фоминское 23б', 'рп': 'Соколов А. А.', 'председатель': 'Литвинов А. В.', 'член_ком1': 'Рябухин А. И.', 'владелец': 'кеиыиыке', 'контакты_владельца': 'иаиепаи', 'пользователь': 'иаепиапи', 'контакты_пользователя': 'вамвяам', 'функциональное_назначение': 'гньгшь', 'право_владения': 'Купли-продажи', 'комментарии_1': 'Пропущено', 'собственность': 'Пропущено', 'комментарии_2': 'Пропущено', 'памятник': 'Да', 'эксплуатация': 'Нет', 'ветхость': 'Нет', 'комментарии_3': 'Пропущено', 'цоколь': 'Да', 'один_собственник': 'Нет', 'комментарии_4': 'Пропущено', 'подвальные_помещения': 'ыерапрвап', 'документы_подвала': 'Не все помещения', 'комментарии_5': 'Пропущено', 'трафик': 'Пешеходный трафик', 'площадь_помещения': 'Пропущено', 'этаж': 'апрмаит', 'этажность': 'Пропущено', 'тип_объекта': 'Цоколь/подвал. Этаж', 'использование_подвала': 'Нет', 'комментарий_6': 'Пропущено', 'соответствие_планировки': 'Да', 'комментарий_7': 'твтгьнг', 'фундамент': 'мпиаиев', 'полы': 'вкеьогань', 'нагрузка': 'втитсн', 'стены': 'огбьаьтьм', 'тип_потолка': 'ьгьть', 'материал_потолка': 'Пропущено', 'тип_пола': 'Пропущено', 'материал_пола': 'Пропущено', 'кровля': 'Пропущено', 'нагрузка_кровли': 'Пропущено', 'конструктивная_схема': 'Пропущено', 'дефекты': 'Пропущено', 'проем': 'Пропущено', 'замена_элементов': 'Пропущено', 'площадь_реконструкции': 'Пропущено', 'пристройка': 'Пропущено', 'потолки': 'Пропущено', 'кровля_переустройство': 'Пропущено', 'тип_строительства': 'Пропущено', 'экспертиза': 'Пропущено', 'требования': 'Пропущено'}

# insert_data_to_excel(file, data)
