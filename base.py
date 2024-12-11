import sqlite3


def create_db():
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            user_id INTEGER PRIMARY KEY,
            name VARCHAR(50),
            number INTEGER,
            adr TEXT,
            [филиал] TEXT,
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
            user_id VARCHAR(25)      

            )
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
    out = []
    for item in row:
        out.append(item)
    cursor.close()
    return out


def update_form_data(user_id, data):
    conn = sqlite3.connect('form_data.db')

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO forms (
                user_id, name, number, adr, [филиал], [адрес], [рп], [площадь_помещения], [этаж], [этажность], [тип_объекта], 
                [использование_подвала], [комментарий_6], [соответствие_планировки], [комментарий_7], [фундамент], [полы], 
                [нагрузка], [стены], [тип_потолка], [материал_потолка], [тип_пола], [материал_пола], [кровля], [нагрузка_кровли], 
                [конструктивная_схема], [дефекты], [возможность], [причина_невозможности], [работы_не_требующие], [нетиповые_работы], 
                [требования_стандарт], [срок_строительства]
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, data.get('name'), data.get('number'), data.get('adr'), data.get('[филиал]'), data.get('[адрес]'), data.get('[рп]'),
            data.get('[площадь_помещения]'), data.get('[этаж]'), data.get('[этажность]'), data.get('[тип_объекта]'),
            data.get('[использование_подвала]'), data.get('[комментарий_6]'), data.get('[соответствие_планировки]'), data.get('[комментарий_7]'),
            data.get('[фундамент]'), data.get('[полы]'), data.get('[нагрузка]'), data.get('[стены]'), data.get('[тип_потолка]'),
            data.get('[материал_потолка]'), data.get('[тип_пола]'), data.get('[материал_пола]'), data.get('[кровля]'), data.get('[нагрузка_кровли]'),
            data.get('[конструктивная_схема]'), data.get('[дефекты]'), data.get('[возможность]'), data.get('[причина_невозможности]'),
            data.get('[работы_не_требующие]'), data.get('[нетиповые_работы]'), data.get('[требования_стандарт]'), data.get('[срок_строительства]')
        ))
    except sqlite3.IntegrityError:
        cursor.execute("""
            UPDATE forms SET 
                name = ?, number = ?, adr = ?, [филиал] = ?, [адрес] = ?, [рп] = ?, [площадь_помещения] = ?, [этаж] = ?, [этажность] = ?, [тип_объекта] = ?,
                [использование_подвала] = ?, [комментарий_6] = ?, [соответствие_планировки] = ?, [комментарий_7] = ?, [фундамент] = ?, [полы] = ?,
                [нагрузка] = ?, [стены] = ?, [тип_потолка] = ?, [материал_потолка] = ?, [тип_пола] = ?, [материал_пола] = ?, [кровля] = ?, [нагрузка_кровли] = ?,
                [конструктивная_схема] = ?, [дефекты] = ?, [возможность] = ?, [причина_невозможности] = ?, [работы_не_требующие] = ?, [нетиповые_работы] = ?,
                [требования_стандарт] = ?, [срок_строительства] = ?
            WHERE user_id = ?
        """, (
            data.get('name'), data.get('number'), data.get('adr'), data.get('[филиал]'), data.get('[адрес]'), data.get('[рп]'),
            data.get('[площадь_помещения]'), data.get('[этаж]'), data.get('[этажность]'), data.get('[тип_объекта]'),
            data.get('[использование_подвала]'), data.get('[комментарий_6]'), data.get('[соответствие_планировки]'), data.get('[комментарий_7]'),
            data.get('[фундамент]'), data.get('[полы]'), data.get('[нагрузка]'), data.get('[стены]'), data.get('[тип_потолка]'),
            data.get('[материал_потолка]'), data.get('[тип_пола]'), data.get('[материал_пола]'), data.get('[кровля]'), data.get('[нагрузка_кровли]'),
            data.get('[конструктивная_схема]'), data.get('[дефекты]'), data.get('[возможность]'), data.get('[причина_невозможности]'),
            data.get('[работы_не_требующие]'), data.get('[нетиповые_работы]'), data.get('[требования_стандарт]'), data.get('[срок_строительства]'),
            user_id
        ))
    conn.commit()
    cursor.close()


def update_non_typical_works(user_id, data):
    conn = sqlite3.connect('form_data.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO non_typical_works (type, period, otvetstvenniy, user_id) VALUES (?, ?, ?, ?)", (data.get('type'), data.get('period'), data.get('otvetstvenniy'), user_id))
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE forms SET type = ?, period = ?, otvetstvenniy = ?, user_id = ?", (data.get('type'), data.get('period'), data.get('otvetstvenniy'), user_id))
    conn.commit()
    cursor.close()


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

