import sqlite3
import aiogram.types as aiotypes
import config
from datatypes import User, Admin
from datatypes import user_changeable_columns



def init_users_db():
    """Создает две таблицы в users.db"""

    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    # создаем Таблицу "Users" пользователей (полевых специалистов):
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Users(
                    id INT NOT NULL UNIQUE,
                    is_working_now INT NOT NULL,
                    is_active INT NOT NULL,
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


def is_user_in_db(user_id: int, echo: bool=False) -> bool:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    check_user = cursor.execute('SELECT * FROM Users WHERE id=?', (user_id,))
    check_user = check_user.fetchone()
    if echo:
        print('check_user_in_db:', not check_user is None)
    if check_user is None:
        return False
    else:
        return True


def add_user(user: User, echo: bool=True):
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    check_user = cursor.execute('SELECT * FROM Users WHERE id=?', (user.id,))
    if check_user.fetchone() is None:
        cursor.execute(f'INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (user.id, user.is_working_now, user.is_active,
                        user.first_name, user.last_name, user.username, user.language_code,
                        user.phone, user.country, user.city, user.birthdate, user.work_email))
        connection.commit()
        if echo:
            print(f'add_user: пользователь с id={user.id} добавлен в db Users')

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
    if not column_name in user_changeable_columns:
        return False
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    check_user = cursor.execute('SELECT * FROM Users WHERE id=?', (user_id,))
    if not check_user.fetchone() is None:
        cursor.execute(f'UPDATE Users SET {column_name} = ? WHERE id = ?', (value, user_id))
        connection.commit()
        connection.close()
        return True
    else:
        connection.close()
        return False

def update_user_from_tg(user_tg: aiotypes.user.User) -> bool:
    user = User(user_tg.id)
    user.fill_from_tg(user_tg)

    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    check = cursor.execute('SELECT * FROM Users WHERE id=?', (user.id,))
    if not check.fetchone() is None:
        cursor.execute(
            f'UPDATE Users SET (first_name, last_name, username, language_code) = (?, ?, ?, ?) WHERE id = ?',
            (user.first_name, user.last_name, user.username, user.language_code, user.id))
        connection.commit()
        connection.close()
        return True
    else:
        connection.close()
        return False


def update_admin(admin: Admin) -> bool:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    check = cursor.execute('SELECT * FROM Admins WHERE id=?', (admin.id,))
    if not check.fetchone() is None:
        cursor.execute(f'UPDATE Admins SET (first_name, last_name, username, language_code) = (?, ?, ?, ?) WHERE id = ?',
                       (admin.first_name, admin.last_name, admin.username, admin.language_code, admin.id))
        connection.commit()
        connection.close()
        return True
    else:
        connection.close()
        return False

def get_user(user_id: int) -> str:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    user = cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchone()
    connection.close()
    return user


def get_greeting_name(user_id: int) -> str:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    user = cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchone()
    connection.close()
    return f'{user[3]} {user[4]}'


def user_is_active(user_id: int) -> int:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    is_active = cursor.execute('SELECT is_active FROM Users WHERE id = ?', (user_id,)).fetchone()
    connection.close()
    return is_active[0]


def get_users():
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    users_list = cursor.execute('SELECT * FROM Users')
    msg = ''
    for u in users_list:
        msg += f'{u[0]}: {u[3]} {u[4]} @{u[5]} ({u[6]}) "в работе"={u[1]}, "is_active={u[2]}"\n\n'

    connection.close()
    return msg


def get_users_in_the_field():
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    users_list = cursor.execute('SELECT * FROM Users WHERE is_working_now = ? and is_active = ?', (1, 1))
    msg = ''
    for u in users_list:
        msg += f'{u[0]}: {u[3]} {u[4]} @{u[5]} ({u[6]})\n\n'

    connection.close()
    return msg

def get_admins():
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    admins_list = cursor.execute('SELECT * FROM Admins')
    msg = ''
    for a in admins_list:
        msg += f'{a[0]}: {a[1]} {a[2]} @{a[3]} ({a[4]})\n\n'

    connection.close()
    return msg


def get_admin(admin_id: int) -> str:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    admin = cursor.execute('SELECT * FROM Admins WHERE id = ?', (admin_id, )).fetchone()
    msg = f'{admin[0]}: {admin[1]} {admin[2]} @{admin[3]} ({admin[4]})'
    connection.close()
    return msg


def users_stat() -> tuple[int, int, int, int]:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    count_users = cursor.execute('SELECT COUNT(*) FROM Users').fetchone()
    count_admins = cursor.execute('SELECT COUNT(*) FROM Admins').fetchone()

    count_users_in_work = cursor.execute('SELECT COUNT(*) FROM Users WHERE is_working_now > 0').fetchone()
    count_active_users = cursor.execute('SELECT COUNT(*) FROM Users WHERE is_active > 0').fetchone()

    connection.close()
    return count_users[0], count_admins[0], count_users_in_work[0], count_active_users[0]


def deactivate_user(user_id: int) -> None:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    cursor.execute(f'UPDATE Users SET is_active = ? WHERE id = ?', (0, user_id))
    connection.commit()
    connection.close()


def activate_user(user_id: int) -> None:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    cursor.execute(f'UPDATE Users SET is_active = ? WHERE id = ?', (1, user_id))
    connection.commit()
    connection.close()


def user_started_work(user_id: int) -> bool:
    '''Делает отметку о том, что специалист начал полевую работу,
    возвращает False, если пользователь не активен и True в штатном случае.
    '''
    pass

def user_completed_work(user_id: int) -> bool:
    '''Делает отметку о том, что специалист закончил полевую работу,
    возвращает False, если работа не была начата и True в штатном случае.
    '''
    pass


# Принудительно производим инициализацию, чтобы сработала при импорте:
init_users_db()
add_admins()
