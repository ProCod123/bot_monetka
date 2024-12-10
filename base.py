import sqlite3

# Подключение к базе данных
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
conn.commit()

        # FOREIGN KEY (id) REFERENCES forms(user_id)

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



def get_form_data(user_id):
    cursor.execute("SELECT * FROM forms WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return dict(zip([description[0] for description in cursor.description], row)) if row else {}


def get_non_typical_works(user_id):
    cursor.execute("SELECT * FROM non_typical_works WHERE user_id = ?", (user_id,))
    row = cursor.fetchall()
    out = []
    for item in row:
        out.append(item)
    return out


def update_form_data(user_id, data):
    try:
        cursor.execute("INSERT INTO forms (user_id, name, number, adr) VALUES (?, ?, ?, ?)", (user_id, data.get('name'), data.get('number'), data.get('adr')))
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE forms SET name = ?, number = ?, adr = ? WHERE user_id = ?", (data.get('name'), data.get('number'), data.get('adr'), user_id))
    conn.commit()

def update_non_typical_works(user_id, data):
    try:
        cursor.execute("INSERT INTO non_typical_works (type, period, otvetstvenniy, user_id) VALUES (?, ?, ?, ?)", (data.get('type'), data.get('period'), data.get('otvetstvenniy'), user_id))
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE forms SET type = ?, period = ?, otvetstvenniy = ?, user_id = ?", (data.get('type'), data.get('period'), data.get('otvetstvenniy'), user_id))
    conn.commit()



# data = {'name' : 'Sasha', 'number' : '1', 'adr' : 'fawefwef'}


# user_id = '1644147255'

# update_form_data('1644147255', {'name': 'Вася'})
# x = get_form_data(user_id)
# print(x)

# data = {'type' : 'roof works3' }
# update_non_typical_works(user_id, data)

# task = get_non_typical_works(user_id)
# print(task)

def delete_non_typical_works_by_user_id(user_id):
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


# delete_non_typical_works_by_user_id(user_id)

# task = get_non_typical_works(user_id)
# print(task)        