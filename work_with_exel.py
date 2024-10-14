import pandas as pd
import win32com.client


file_zapusk = '../Запуск 07.10.xlsm'


def get_task(filename, sheet_name='ЗАПУСК', apo_status_col=154, adress_col=3, name_col=103):
    """АПО статус EY 155
       Адрес D 3
       РП 103
    """
    df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=2)

    output = {}
    for index, row in df.iterrows():
        if row.iloc[apo_status_col] == 'вложить':
            name = row.iloc[name_col]
            path = str(row.iloc[0]) + ' ' + row.iloc[1] + ' ' + row.iloc[2] + ' ' + row.iloc[adress_col]
            if name in output:
                output[name].append(path)
            else:
                output[name] = [path]

    return output


def get_id(name):
    df = pd.read_excel(file_zapusk, sheet_name='Телеграм', nrows=30)
    for index, row in df.iterrows():
        if row.iloc[1] == name:
            id = row.iloc[2]
            return id # Возвращаем значение, как только оно найдено
    return None # Возвращаем None, если не найдено


def run_vba_macro(excel_file, module_name, macro_name):
    try:
        # Получаем существующий экземпляр Excel, если он открыт,
        # иначе создаем новый
        excel = win32com.client.DispatchEx("Excel.Application")

        # Открываем файл, если он не открыт
        if excel_file not in [wb.FullName for wb in excel.Workbooks]:
            workbook = excel.Workbooks.Open(excel_file)

        # Находим модуль и макрос 
        module = workbook.VBProject.VBComponents(module_name)
        macro = module.CodeModule.Lines(1, module.CodeModule.CountOfLines)
        
        excel.Run(macro_name) # Запускаем макрос
        workbook.Save() # Сохраняем изменения в файле
        workbook.Close() # Закрываем файл
        
        print(f"VBA-макрос '{macro_name}' в модуле '{module_name}' успешно выполнен в файле '{excel_file}'")

    except Exception as e:
        print(f"Ошибка при выполнении VBA-макроса: {e}")
        
    finally:
        if excel:
            excel.Quit() # Закрываем Excel, если он был создан


import openpyxl

def insert_data_to_excel(file_name, data_dict, sheet_name):
    try:
        workbook = openpyxl.load_workbook(file_name, keep_vba=True)
    except FileNotFoundError:
        workbook = openpyxl.Workbook()

    worksheet = workbook[sheet_name] # Получение листа
    
    # Соответствие ключей словаря ячейкам
    cell_mapping = {}
    if sheet_name == '1':
        cell_mapping = {
            "председатель": "B15",
            "член_ком1": "B20",
            "рп": "B22",
        }
    elif sheet_name == '2':
        cell_mapping = {
            "адрес": "B6",
            "владелец": "B7",
            "контакты_владельца": "B8",
            "пользователь": "B10",
            "контакты_пользователя": "B11",
            "функциональное_назначение": "C13",
            "право_владения": "E15",
            "комментарии_1": "B18",
            "собственность": "E19",
            "комментарии_2": "B22",
            "памятник": "F23",
            "эксплуатация": "F24",
            "ветхость": "F25",
            "комментарии_3": "B26",
            "цоколь": "F27",
            "один_собственник": "F28",
            "комментарии_4": "B29",
            "подвальные_помещения": "C30",
            "документы_подвала": "E33",
            "комментарии_5": "B34",
            "трафик": "E35",
        }
    
    # Запись данных в ячейки
    for key, value in data_dict.items():
        if key in cell_mapping.keys():
            cell = cell_mapping[key]
            print(cell)
            worksheet[cell] = value

    workbook.save(file_name) # Сохранение изменений
    print(f"Данные успешно вставлены в файл '{file_name}'.")


file = '../Объекты/1 СПБ ЛО, г.п. Мга Железнодорожная, д. 34а/Акты/АПО/АПО СПБ ЛО, г.п. Мга Железнодорожная, д. 34а.xlsm'
data = {'id': 1644147255, 'филиал': 'МСК', 'адрес': '154 МСК МО, Первомайское Фоминское 23б', 'рп': 'Соколов', 'председатель': 'Литвинов А. В.', 'член_ком1': 'Рябухин А. И.', 'владелец': 'regferg', 'контакты_владельца': 'desfzsdf', 'пользователь': 'Пропущено', 'контакты_пользователя': 'Пропущено', 'функциональное_назначение': 'Пропущено', 'право_владения': 'Аренда', 'комментарии_1': '1', 'собственность': 'Частная собственность', 'комментарии_2': '2', 'памятник': 'Да', 'эксплуатация': 'Да', 'ветхость': 'Да', 'комментарии_3': '3', 'цоколь': 'Да', 'один_собственник': 'Да', 'комментарии_4': '4', 'подвальные_помещения': 'vsdvd', 'документы_подвала': 'Все помещения', 'комментарии_5': '5', 'трафик': 'Пешеходный трафик', 'площадь_помещения': '51615', 'этаж': 's\\fsd', 'этажность': 'Пропущено', 'тип_объекта': 'Иные объекты', 'использование_подвала': 'Да', 'комментарий_6': 'Пропущено', 'соответствие_планировки': 'Пропущено', 'комментарий_7': 'Пропущено', 'фундамент': 'Пропущено', 'полы': 'Пропущено', 'нагрузка': 'Пропущено', 'стены': 'Пропущено', 'тип_потолка': 'Пропущено', 'материал_потолка': 'Пропущено', 'тип_пола': 'Пропущено', 'материал_пола': 'Пропущено', 'кровля': 'Пропущено', 'конструктивная_схема': 'Пропущено', 'дефекты': 'Пропущено', 'проем': 'Пропущено', 'замена_элементов': 'Пропущено', 'площадь_реконструкции': 'Пропущено', 'пристройка': 'Пропущено', 'потолки': 'Пропущено', 'полы_объем': 'Пропущено', 'кровля_переустройство': 'Пропущено', 'тип_строительства': 'Пропущено', 'экспертиза': 'Да', 'требования': 'Пропущено'}