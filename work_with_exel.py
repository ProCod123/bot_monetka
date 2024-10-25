import pandas as pd
import win32com.client
import pythoncom
import openpyxl
from openpyxl.drawing.image import Image

from workers import ID



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

# находим имя соответствующее id
def get_name(id):
    for item in ID.items():
        if str(id) == item[1]:
            return item[0]
    return None


def run_vba_macro(excel_file, module_name, macro_name):

    excel = None
    try:
        pythoncom.CoInitialize()
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
        pythoncom.CoUninitialize()




import openpyxl
from openpyxl.drawing.image import Image
import pythoncom

def insert_image_to_cell(file_path, sheet_name, cell_reference, image_name):


    try:
        pythoncom.CoInitialize() 
        workbook = openpyxl.load_workbook(file_path, read_only=False)
        worksheet = workbook[sheet_name]

        # Загружаем картинку
        img = Image(image_name)
        print(f"Изображение загружено: {image_name}")

        # Устанавливаем размер картинки
        img.width = img.width * 0.5 
        img.height = img.height * 0.5 
        print(f"Размер изображения изменен: {img.width}x{img.height}")

        # Вставляем картинку в ячейку
        worksheet.add_image(img, cell_reference)
        print(f"Изображение добавлено в ячейку: {cell_reference}")

        # Сохраняем изменения
        workbook.save(file_path)
        print(f"Файл сохранен: {file_path}")

        print(f"Подпись добавлена!")

    except Exception as e:
        print(f"При добавления подписи: {e}")
    finally:
        pythoncom.CoUninitialize() 



# Пример использования
file_path = 'C:/Users/user/Desktop/раб/bot/АПО.xlsx' 
sheet_name = '11'                # Замените на ваш лист
cell_reference = 'D47'              # Замените на вашу ячейку
image_name = 'C:/Users/user/Desktop/раб/bot/podpisi/Соколов.png'

# insert_image_to_cell(file_path, sheet_name, cell_reference, image_name)
