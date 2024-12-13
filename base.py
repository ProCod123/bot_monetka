import sqlite3


def create_db():
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            user_id INTEGER PRIMARY KEY,
            objects_path TEXT,
            name VARCHAR(50),
            number INTEGER,
            adr TEXT,
            [филиал] TEXT,
            [РОР] TEXT,
            [ИСК] TEXT,
            [адрес] TEXT,
            [рп] TEXT,


            [площадь_помещения] TEXT,
            [этаж] TEXT,
            [этажность] TEXT,
            [тип_объекта] TEXT,
            [использование_подвала] TEXT,
            [комментарий_6] TEXT,
            [соответствие_планировки] TEXT,
            [комментарий_7] TEXT,
            [фундамент] TEXT,
            [полы] TEXT,
            [нагрузка] TEXT,
            [стены] TEXT,
            [тип_потолка] TEXT,
            [материал_потолка] TEXT,
            [тип_пола] TEXT,
            [материал_пола] TEXT,
            [кровля] TEXT,
            [нагрузка_кровли] TEXT,
            [конструктивная_схема] TEXT,
            [дефекты] TEXT,


            [возможность] TEXT,
            [причина_невозможности] TEXT,
            [работы_не_требующие] TEXT,
            [нетиповые_работы] TEXT,
            [требования_стандарт] TEXT,
            [срок_строительства] TEXT
            );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS non_typical_works (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type VARCHAR(255),
            period VARCHAR(25),
            otvetstvenniy VARCHAR(25),
            user_id VARCHAR(25),
            object_adress TEXT
            );
            ''')

    conn.commit()
    cursor.close()


def get_form_data(user_id):
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM forms WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    return dict(zip([description[0] for description in cursor.description], row)) if row else {}


def get_non_typical_works(user_id):
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM non_typical_works WHERE user_id = ?", (user_id,))
    row = cursor.fetchall()
    out = {'нетиповые_работы' : []}
    
    for item in row:
        out['нетиповые_работы'].append({'тип_работ': item[1], 'срок': item[2], 'ответственный': item[3]}) 
                                       
    cursor.close()
    return out


def update_form_data(user_id, data):
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()

    columns = []
    values = [user_id]
    placeholders = ['?'] * len(values) # Создаем список заполнителей для значений


    for column in [
        'objects_path', 'name', 'number', 'adr', '[филиал]', '[РОР]', '[ИСК]', '[адрес]', '[рп]', '[площадь_помещения]', '[этаж]', '[этажность]', '[тип_объекта]',
        '[использование_подвала]', '[комментарий_6]', '[соответствие_планировки]', '[комментарий_7]', '[фундамент]', '[полы]',
        '[нагрузка]', '[стены]', '[тип_потолка]', '[материал_потолка]', '[тип_пола]', '[материал_пола]', '[кровля]', '[нагрузка_кровли]',
        '[конструктивная_схема]', '[дефекты]', '[возможность]', '[причина_невозможности]', '[работы_не_требующие]', '[нетиповые_работы]',
        '[требования_стандарт]', '[срок_строительства]'
    ]:
      if column in data and data[column] is not None:
        columns.append(column)
        values.append(data[column])
        placeholders.append('?')

    if not columns: #Если data пустой
        print("Нет данных для обновления")
        return


    sql_insert = f"""
        INSERT INTO forms ({', '.join(['user_id'] + columns)}) 
        VALUES ({', '.join(placeholders)})
        ON CONFLICT(user_id) DO UPDATE SET {', '.join([f'{col} = ?' for col in columns])}
    """


    try:
        cursor.execute(sql_insert, values + values[1:]) # values + values[1:] для UPDATE
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка SQL: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Новая запись создается только если вводится пара из типа работ и адреса не существующих в таблице

def update_non_typical_works(user_id, data):
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()
    try:
        # Считываем данные последней записи
        cursor.execute("SELECT id, object_adress, type FROM non_typical_works WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
        last_record = cursor.fetchone()

        if last_record:
            last_id = last_record[0]
            last_object_adress = last_record[1]
            last_type = last_record[2]
            
            # Проверяем, нужно ли создавать новую запись, учитывая только переданные поля
            create_new_entry = False
            if 'object_adress' in data and data['object_adress'] != last_object_adress:
              create_new_entry = True
            elif 'type' in data and data['type'] != last_type:
              create_new_entry = True


            if create_new_entry:
                # Если значения object_adress или type отличаются, добавляем новую запись
                cursor.execute("""
                    INSERT INTO non_typical_works (type, period, otvetstvenniy, object_adress, user_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (data.get('type'), data.get('period'), data.get('otvetstvenniy'), data.get('object_adress'), user_id))
            else:
                # Если значения совпадают, обновляем запись.
                update_values = []
                for field, value in data.items():
                    if value is not None:
                        update_values.append((field, value))
                
                if update_values: # Проверяем, есть ли вообще что-то для обновления
                    set_clause = ', '.join([f"{field}=?" for field, value in update_values])
                    cursor.execute(f"""UPDATE non_typical_works SET {set_clause} WHERE id = ?""", [value for _, value in update_values] + [last_id])

        else:
            # Если таблица пуста, вставляем новую запись
            cursor.execute("""
                INSERT INTO non_typical_works (type, period, otvetstvenniy, object_adress, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (data.get('type'), data.get('period'), data.get('otvetstvenniy'), data.get('object_adress'), user_id))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()





def delete_non_typical_works_by_user_id(user_id):
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()
    """Удаляет все записи из non_typical_works для указанного user_id."""
    try:
        cursor.execute("DELETE FROM non_typical_works WHERE user_id = ?", (user_id,))
        conn.commit()
        print(f"Удалено {cursor.rowcount} записей для user_id = {user_id}")
    except sqlite3.Error as e:
        conn.rollback() # Отмена транзакции в случае ошибки
        print(f"Ошибка базы данных при удалении записей: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
    cursor.close()    


def get_row_last_id(user_id):
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM non_typical_works WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()

    cursor.close()
    return row
        


create_db()

# update_form_data('1644147255', {'name' : 'ferfre'})

print(get_form_data('1483719750'))


# update_non_typical_works('1644147255', {'period' : 'до АПП'})
# update_form_data('1644147255', {'нетиповые_работы': 'Да'})

# delete_non_typical_works_by_user_id('1644147255')
# print(get_non_typical_works('1644147255'))

# print(get_row_last_id('1644147255'))


