import sqlite3
import aiogram.types as aiotypes
import config
from datatypes import User, Admin
from datatypes import user_changeable_columns
import settings


def init_project_db():
    """Создает две таблицы в project.db"""

    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()

    # создаем Таблицу "Points" точек проекта:
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Points(
                    PointID TEXT NOT NULL UNIQUE,
                    ComplectID TEXT,
                    datetime_start TEXT,
                    datetime_end TEXT,
                    N_WGS84_plan REAL NOT NULL,
                    E_WGS84_plan REAL NOT NULL,
                    N_WGS84_fact REAL,
                    E_WGS84_fact REAL,
                    H_WGS84 REAL,
                    LON_UTM REAL,
                    LAT_UTM REAL,
                    Z_UTM REAL,
                    Comments TEXT
                    );''')

    # создаем Таблицу "Devices" полевых комплектов приборов:
    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS Devices(
                        ComplectID TEXT NOT NULL UNIQUE,
                        status TEXT,
                        PointID TEXT,
                        UserID INT,
                        datetime_start TEXT
                        );''')
    # <ComplectID> is <busy> at <PointID> by <UserID> since <datetime_start>
    connection.commit()
    connection.close()


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


def fill_points(PointsID: list[str], N_WGS84: list[str], E_WGS84: list[str]) -> None:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()
    for pid, lat, lon in zip(PointsID, N_WGS84, E_WGS84):
        cursor.execute('INSERT INTO Points (PointID, N_WGS84_plan, E_WGS84_plan) VALUES (?, ?, ?)',
                       (pid, lat, lon))
    connection.commit()
    connection.close()


def fill_complects(ComplectsID: list[str]) -> None:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()
    for cid in ComplectsID:
        cursor.execute('INSERT INTO Devices (ComplectID, status) VALUES (?, ?)',
                       (cid, 'свободен'))
    connection.commit()
    connection.close()


def clear_points() -> None:
    # очищает таблицу со списком приборов, взятых в поле на текущее задание:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Points')

    connection.commit()
    connection.close()


def refill_points(PointsID: list[str], N_WGS84: list[str], E_WGS84: list[str]) -> None:
    # очищает и заново заполняет:
    clear_points()
    fill_points(PointsID, N_WGS84, E_WGS84)


def clear_complects() -> None:
    # очищает таблицу со списком приборов, взятых в поле на текущее задание:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Devices')

    connection.commit()
    connection.close()


def refill_complects(ComplectsID: list[str]) -> None:
    # очищает и заново заполняет:
    clear_complects()
    fill_complects(ComplectsID)


def get_points_started() -> str:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()
    try:
        selected_points = cursor.execute('SELECT PointID, ComplectID, datetime_start, Comments '
                                         'FROM Points WHERE datetime_start NOT NULL')
    except sqlite3.DatabaseError as exc:
        connection.close()
        return f'Извините, возникла ошибка при работе с БД:\n{exc}'
    msg = ''
    selected_points = list(selected_points)
    if len(selected_points) > 0:
        for pid in selected_points:
            msg += f'{pid[0]}: установлен {pid[1]} с {pid[2]} ({pid[3]})\n\n'

    connection.close()
    return msg


def get_points_rest() -> str:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()
    try:
        selected_points = cursor.execute('SELECT PointID, N_WGS84_plan, E_WGS84_plan '
                                         'FROM Points WHERE datetime_start IS NULL')
    except sqlite3.DatabaseError as exc:
        connection.close()
        return f'Извините, возникла ошибка при работе с БД:\n{exc}'
    msg = ''
    selected_points = list(selected_points)
    if len(selected_points) > 0:
        for pid in selected_points:
            msg += f'{pid[0]} ({pid[1]} {pid[2]}) без прибора\n\n'
    connection.close()
    return msg


def get_busy_complects() -> str:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()
    try:
        selected = cursor.execute('SELECT ComplectID, PointID FROM Devices WHERE status = ?',
                                  ('установлен',))
    except sqlite3.DatabaseError as exc:
        connection.close()
        return f'Извините, возникла ошибка при работе с БД:\n{exc}'
    msg = ''
    selected = list(selected)
    if len(selected) > 0:
        for cid in selected:
            msg += f'{cid[0]} установлен в {cid[1]}\n'
    else:
        msg = 'Нет установленных комплектов.'

    connection.close()
    return msg


def get_free_complects() -> str:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()
    try:
        selected = cursor.execute('SELECT ComplectID FROM Devices WHERE status = ?',
                                  ('свободен',))
    except sqlite3.DatabaseError as exc:
        connection.close()
        return f'Извините, возникла ошибка при работе с БД:\n{exc}'
    selected = list(selected)
    if len(selected) > 0:
        msg = ''
        for j, cid in enumerate(selected[:-1]):
            if j < settings.bot_max_show_complects:
                msg += f'{cid[0]},  '
            else:
                msg += '..., '
                break
        msg += f'{selected[-1][0]}.'
    else:
        msg = 'Нет свободных комплектов.'
    connection.close()
    return msg


def get_point(point_id: str) -> list[str]:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()
    point = cursor.execute('SELECT * FROM Points WHERE PointID = ?', (point_id,)).fetchone()
    point = list(point)
    connection.close()
    return point


def get_complect(complect_id: str) -> list[str]:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()
    complect = cursor.execute('SELECT * FROM Devices WHERE ComplectID = ?', (complect_id,)).fetchone()
    complect = list(complect)
    connection.close()
    return complect


def set_point_start(point_id: str, lat_fact: float, lon_fact: float,
                    complect_id: str, user_id: int, datetime_start: str) -> str:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()

    pid_check = cursor.execute('SELECT * FROM Points WHERE PointID=?', (point_id,))
    if pid_check.fetchone() is None:
        connection.close()
        return f'Извините, точка {point_id} в базе не найдена, или отсутствует подключение.'

    try:
        # Запись: в Таблицу Points
        cursor.execute('UPDATE Points SET '
                       '(ComplectID, datetime_start, N_WGS84_fact, E_WGS84_fact, Comments) = (?, ?, ?, ?, ?) WHERE PointID = ?',
                       (complect_id, str(datetime_start), lat_fact, lon_fact, str(user_id), point_id))
    except sqlite3.DatabaseError as exc:
        connection.close()
        return f'Извините, возникла ошибка при работе с базой данных точек проекта:\n{exc}'

    cid_check = cursor.execute('SELECT * FROM Devices WHERE ComplectID=?', (complect_id,))

    if cid_check.fetchone() is None:
        connection.close()
        return f'Извините, комплект {complect_id} в базе не найден, или отсутствует подключение.'

    try:
        # Запись: в Таблицу Devices
        cursor.execute(
            'UPDATE Devices SET (status, PointID, UserID, datetime_start) = (?, ?, ?, ?) WHERE ComplectID = ?',
            ('установлен', point_id, user_id, str(datetime_start), complect_id))
    except sqlite3.DatabaseError as exc:
        connection.close()
        return f'Извините, возникла ошибка при работе с базой данных приборов:\n{exc}'

    connection.commit()
    connection.close()
    return f'Прибор {complect_id} в точке {point_id} установлен.'


def set_point_end(point_id: str, datetime_end: str) -> str:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()

    pid_check = cursor.execute('SELECT * FROM Points WHERE PointID=?', (point_id,))
    if pid_check.fetchone() is None:
        connection.close()
        return f'Извините, точка {point_id} в базе не найдена, или отсутствует подключение.'
    try:
        cursor.execute(
            'UPDATE Points SET datetime_end = ? WHERE PointID = ?',
            (str(datetime_end), point_id))
    except sqlite3.DatabaseError as exc:
        connection.close()
        return f'Извините, возникла ошибка при работе с БД:\n{exc}'

    connection.commit()
    connection.close()
    return f'Регистрация в точке {point_id} завершена.'


def set_complect_free(complect_id: str) -> str:
    connection = sqlite3.connect('databases/project.db')
    cursor = connection.cursor()

    cid = cursor.execute('SELECT * FROM Devices WHERE ComplectID=?', (complect_id,))
    if cid.fetchone() is None:
        connection.close()
        return f'Извините, прибор {complect_id} в базе не найден, или отсутствует подключение.'
    try:
        cursor.execute(
            'UPDATE Devices SET status = ? WHERE ComplectID = ?',
            ('свободен', complect_id))
    except sqlite3.DatabaseError as exc:
        connection.close()
        return f'Извините, возникла ошибка при работе с БД:\n{exc}'

    connection.commit()
    connection.close()
    return f'Принято: прибор {complect_id} отмечен как свободный.'


'''Далее блок CRUD-функций для Users и Admins
=============================================='''


def add_admins():
    """Впервые в db прописываются только id (telegram.id) admin-пользователей,
    далее при их подключении по их желанию, подтягиваются данные и заполняются остальные поля."""
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    for admin_id in config.admins:
        check_user = cursor.execute('SELECT * FROM Admins WHERE id=?', (admin_id,))
        if check_user.fetchone() is None:
            # добавляем:
            a = Admin(id=admin_id)
            cursor.execute('INSERT INTO Admins VALUES (?, ?, ?, ?, ?)',
                           (a.id, a.first_name, a.last_name, a.username, a.language_code))

    connection.commit()
    connection.close()


def is_user_in_db(user_id: int, echo: bool = False) -> bool:
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


def add_user(user: User, echo: bool = True):
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()

    check_user = cursor.execute('SELECT * FROM Users WHERE id=?', (user.id,))
    if check_user.fetchone() is None:
        cursor.execute('INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
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
        cursor.execute('INSERT INTO Admin VALUES (?, ?, ?, ?, ?)',
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
            'UPDATE Users SET (first_name, last_name, username, language_code) = (?, ?, ?, ?) WHERE id = ?',
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
        cursor.execute('UPDATE Admins SET (first_name, last_name, username, language_code) = (?, ?, ?, ?) WHERE id = ?',
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
    admin = cursor.execute('SELECT * FROM Admins WHERE id = ?', (admin_id,)).fetchone()
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
    cursor.execute('UPDATE Users SET is_active = ? WHERE id = ?', (0, user_id))
    connection.commit()
    connection.close()


def activate_user(user_id: int) -> None:
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE Users SET is_active = ? WHERE id = ?', (1, user_id))
    connection.commit()
    connection.close()


def user_started_work(user_id: int) -> bool:
    '''Делает отметку о том, что специалист начал полевую работу,
    возвращает False, если пользователь не активен и True в штатном случае.
    '''
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    is_active = cursor.execute('SELECT is_active FROM Users WHERE id = ?', (user_id,)).fetchone()
    if is_active[0] == 1:
        cursor.execute('UPDATE Users SET is_working_now = ? WHERE id = ?', (1, user_id))
        connection.commit()
        connection.close()
    else:
        connection.close()
        return False


def user_completed_work(user_id: int) -> bool:
    '''Делает отметку о том, что специалист закончил полевую работу,
    возвращает False, если работа не была начата и True в штатном случае.
    '''
    connection = sqlite3.connect('databases/users.db')
    cursor = connection.cursor()
    is_working_now = cursor.execute('SELECT is_working_now FROM Users WHERE id = ?', (user_id,)).fetchone()
    if is_working_now[0] == 1:
        cursor.execute('UPDATE Users SET is_working_now = ? WHERE id = ?', (0, user_id))
        connection.commit()
        connection.close()
        return True
    else:
        connection.close()
        return False


# Принудительно производим инициализацию, чтобы сработала при импорте:
init_project_db()
init_users_db()
add_admins()
