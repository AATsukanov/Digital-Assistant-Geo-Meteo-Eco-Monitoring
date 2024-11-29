from dataclasses import dataclass
import aiogram.types as aiotypes
import pandas as pd
import numpy as np
import datetime
import os
import json

import settings

class Task:

    def __init__(self):
        self.ProjectName: str = ''
        self.nPoints: int = 0  # количество проектных точек
        self.fname_project_points: str = ''  # *.xlsx файл
        self.recommended_group_of_devices = set(settings.devices_groups)
        self.Point_ID = np.array([])
        self.N_WGS84 = np.array([])
        self.E_WGS84 = np.array([])
        self.TextTaskDetails: str = ''
        self.date = datetime.date.today()

    def load(self, fname: str, echo=False) -> bool:
        if not os.path.isfile(fname):
            print(f'Task.load: файл {fname} не найден')
            return False

        try:
            data_pd = pd.read_excel(fname)
        except Exception as exc:
            print(f'Task.load: ошибка при чтении файла {fname} методом pd.read_excel\n{exc}')
            return False
        if echo:
            print(f'Task.load: столбцы = {data_pd.columns}')

        # пока нужны только столбцы 'Point_ID', 'N-WGS84', 'E-WGS84':
        self.Point_ID = np.array(data_pd['Point_ID'])
        self.N_WGS84 = np.array(data_pd['N-WGS84'])
        self.E_WGS84 = np.array(data_pd['E-WGS84'])

        # если все удачно сохраним путь к исходной Таблице:
        self.fname_project_points = fname
        self.nPoints = len(self.Point_ID)
        print(f'Загружено {self.nPoints} проектных точек.')
        return True

    def reset(self):
        self.ProjectName: str = ''
        self.nPoints: int = 0
        self.fname_project_points: str = ''
        self.recommended_group_of_devices = set(settings.devices_groups)
        self.Point_ID = np.array([])
        self.N_WGS84 = np.array([])
        self.E_WGS84 = np.array([])
        self.data_pd: pd.DataFrame = pd.DataFrame([])
        self.TextTaskDetails: str = ''
        self.date = datetime.date.today()

    def save_as_json(self, fname: str) -> None:
        json.dumps()


@dataclass
class User:
    id: int
    is_working_now: int = 0  # 0 - не в поле, 1 - в поле (или потом 10 -- начал работу, 100 -- завершил работу)
    is_active: int = 1  # аналог блокировки: 0 - не работает, 1 - работает
    first_name: str = ''
    last_name: str = ''
    username: str = '(не указан)'
    language_code: str = 'ru'
    phone: str = '(пусто)'
    country: str = '(пусто)'
    city: str = '(пусто)'
    birthdate: str = 'ГГГГ-ММ-ДД'
    work_email: str = '(пусто)'

    def fill_from_tg(self, user: aiotypes.user.User) -> None:
        if 'first_name' in user:
            self.first_name = user['first_name']
        if 'last_name' in user:
            self.last_name = user['last_name']
        if 'username' in user:
            self.username = user['username']
        if 'language_code' in user:
            self.language_code = user['language_code']


@dataclass
class Admin:
    id: int
    first_name: str = '(пусто)'
    last_name: str = '(пусто)'
    username: str = '(пусто)'
    language_code: str = 'ru'

    def update_from_tg(self, user: aiotypes.user.User, echo: bool = False) -> None:
        if echo:
            print(f'Заполняем админ-пользователя из Telegram from_user = {user}')
        if 'first_name' in user:
            self.first_name = user['first_name']
        if 'last_name' in user:
            self.last_name = user['last_name']
        if 'username' in user:
            self.username = user['username']
        if 'language_code' in user:
            self.language_code = user['language_code']


user_all_columns = ['id', 'is_working_now', 'is_active', 'first_name', 'last_name', 'username', 'language_code',
                    'phone', 'country', 'city', 'birthdate', 'work_email']

user_changeable_columns = ['first_name', 'last_name', 'phone', 'country', 'city', 'birthdate', 'work_email']
