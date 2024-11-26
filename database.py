import sqlite3
import config
import data_classes
from data_classes import User, Admin


def init_users_db():
    """Создает две таблицы в users.db"""

    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    # создаем Таблицу "Users" пользователей (полевых специалистов):
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Users(
                    id INT NOT NULL UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT NOT NULL,
                    language_code TEXT,
                    phone TEXT,
                    country TEXT,
                    city TEXT,
                    birthdate TEXT,
                    work_email TEXT
                    );''')

    # создаем Таблицу "Admins" admin-пользователей (координационный центр):
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Admins(
                    id INT NOT NULL UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    language_code TEXT
                    );''')

    connection.commit()
    connection.close()


def add_admins():
    '''Впервые в db прописываются только id (telegram.id) admin-пользователей,
    далее при их подключении по их желанию, подтягиваются данные и заполняются остальные поля.'''
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    for admin_id in config.admins:
        check_user = cursor.execute('SELECT * FROM Admins WHERE id=?', (admin_id,))
        if check_user.fetchone() is None:
            # добавляем:
            a = Admin(id=admin_id)
            cursor.execute(f'INSERT INTO Admins VALUES (?, ?, ?, ?, ?)',
                           (a.id, a.first_name, a.last_name, a.username, a.language_code))

    connection.commit()
    connection.close()

def check_user_in_db(user_id: int) -> bool:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    check_user = cursor.execute('SELECT * FROM Users WHERE id=?', (user_id,))
    if check_user.fetchone() is None:
        return False
    else:
        return True

def add_user(user: User):
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    check_user = cursor.execute('SELECT * FROM Users WHERE id=?', (user.id,))
    if check_user.fetchone() is None:
        cursor.execute(f'INSERT INTO User VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (user.id, user.first_name, user.last_name, user.username, user.language_code,
                        user.phone, user.country, user.city, user.birthdate, user.work_email))
        connection.commit()

    connection.close()


def add_admin(admin: Admin):
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    check_user = cursor.execute('SELECT * FROM Admins WHERE id=?', (admin.id,))
    if check_user.fetchone() is None:
        cursor.execute(f'INSERT INTO Admin VALUES (?, ?, ?, ?, ?)',
                       (admin.id, admin.first_name, admin.last_name, admin.username, admin.language_code))
        connection.commit()

    connection.close()


def update_user(user_id: int, column_name: str, value: str) -> bool:
    if not column_name in data_classes.user_changeable_columns:
        return False
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    check_user = cursor.execute('SELECT * FROM Users WHERE id=?', (user_id,))
    if check_user.fetchone() is None:
        cursor.execute(f'UPDATE Users SET {column_name} = ? WHERE id = ?', (value, user_id))
        connection.commit()
        connection.close()
        return True
    else:
        connection.close()
        return False


def show_users():
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    users_list = cursor.execute('SELECT * FROM Users')
    msg = ''
    for u in users_list:
        msg += f'{u[0]}: {u[1]} {u[2]} @{u[3]} ({u[4]})\n'

    connection.close()
    return msg


def show_admins():
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    admins_list = cursor.execute('SELECT * FROM Admins')
    msg = ''
    for a in admins_list:
        msg += f'{a[0]}: {a[1]} {a[2]} @{a[3]} ({a[4]})\n'

    connection.close()
    return msg


def users_stat() -> tuple[int, int]:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    count_users = cursor.execute('SELECT COUNT(*) FROM Users').fetchone()
    count_admins = cursor.execute('SELECT COUNT(*) FROM Admins').fetchone()

    connection.close()
    return count_users, count_admins


# Принудительно производим инициализацию, чтобы сработала при импорте:
init_users_db()
add_admins()
