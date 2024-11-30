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
        self.ProjectName: str = '(не указано)'
        self.nPoints: int = 0  # количество проектных точек
        self.nComplects: int = 0  # количество приборов на полевой день
        self.fname_project_points: str = ''  # *.xlsx файл
        self.recommended_group_of_devices = set(settings.devices_groups)
        self.subgroups_dict: dict = {}
        self.Point_ID = np.array([])
        self.N_WGS84 = np.array([])
        self.E_WGS84 = np.array([])
        self.map_image: str = ''
        self.df_of_complects = pd.DataFrame([])
        self.TaskDetails: str = ''
        self.date: str = str(datetime.date.today())

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

    def load_table_of_complects(self, fname: str, echo=False) -> bool:
        if not os.path.isfile(fname):
            print(f'Task.load_table_of_complects: файл {fname} не найден')
            return False
        try:
            data_pd = pd.read_excel(fname)
        except Exception as exc:
            print(f'Task.load_table_of_complects: ошибка при чтении файла {fname} методом pd.read_excel\n{exc}')
            return False
        if echo:
            print(f'Task.load_table_of_complects: столбцы = {data_pd.columns}')

        # нужны столбцы 'ComplectID', 'date_of_completion', 'GroupID':
        data_pd.sort_values(by=['date_of_completion', 'ComplectID'], inplace=True)
        data_pd = data_pd[['ComplectID', 'GroupID']]

        self.df_of_complects = data_pd.drop_duplicates(subset='ComplectID', keep='last', inplace=False)

        self.nComplects = len(self.df_of_complects["ComplectID"])
        print(f'Загружено {self.nComplects} комплектов приборов.')
        return True

    def create_subgroups_of_devices(self, echo: bool = False) -> None:
        """ Собирает идентификаторы комплектов/приборов их групп и подгрупп в удобный для tg-бота словарь:
            dict{группа: dict{погруппа: list[комплекты]}}
        """
        # создаем дополнительный столбец с названиями подгрупп:
        self.df_of_complects['SubGroups'] = self.df_of_complects['GroupID']
        for j, cid in enumerate(self.df_of_complects['ComplectID']):
            if str(cid).isdigit():
                if len(cid) < 2:
                    sub = '1-9'
                elif len(cid) < 3:
                    sub = f'{cid[0]}0-{cid[0]}9'
                else:
                    sub = '100+'
            else:
                if len(cid) < 4:
                    # еще как вариант: sub = f'{cid[:2]}[0-9]'
                    sub = f'{cid[:2]}0-{cid[:2]}9'
                else:
                    sub = f'{cid[0]}100+'
            self.df_of_complects.iloc[j, self.df_of_complects.columns.get_loc('SubGroups')] = sub

        # обнуляем словарь:
        self.subgroups_dict: dict = {}
        for GroupID in sorted(list(set(self.df_of_complects['GroupID']))):
            sub = {}
            for subgroup in sorted(list(set(self.df_of_complects[self.df_of_complects['GroupID'] == GroupID]['SubGroups']))):
                complects_list = self.df_of_complects[self.df_of_complects['SubGroups'] == subgroup]
                complects_list = sorted(list(complects_list['ComplectID']))
                if len(complects_list) > 0:
                    sub[str(subgroup)] = complects_list
            if not sub == {}:
                self.subgroups_dict[str(GroupID)] = sub
        if echo:
            print(self.subgroups_dict)

    def reset(self):
        self.ProjectName: str = '(не указано)'
        self.nPoints: int = 0
        self.nComplects: int = 0
        self.fname_project_points: str = ''
        self.recommended_group_of_devices = set(settings.devices_groups)
        self.subgroups_dict: dict = {}
        self.Point_ID = np.array([])
        self.N_WGS84 = np.array([])
        self.E_WGS84 = np.array([])
        self.map_image: str = ''
        self.df_of_complects = pd.DataFrame([])
        self.TaskDetails: str = ''
        self.date: str = str(datetime.date.today())

    def save_as_json(self, fname: str) -> None:
        # аккуратно собираем словарь:
        obj: dict[str: dict[str: list[str]]] = {}
        obj['ProjectName']: str = self.ProjectName
        obj['nPoints']: int = self.nPoints
        obj['nComplects']: int = self.nComplects
        obj['recommended_group_of_devices']: list[str] = self.recommended_group_of_devices
        obj['subgroups_dict']: dict = self.subgroups_dict
        obj['map_image']: str = self.map_image
        obj['TaskDetails']: str = self.TaskDetails
        obj['date']: str = self.date

        # преобразуем в json и сохраняем:
        with open(fname, 'w') as file:
            json.dump(obj, file)


@dataclass
class User:
    id: int
    is_working_now: int = 0  # 0 - не в поле, 1 - в поле (или потом 10 -- начал работу, 100 -- завершил работу)
    is_active: int = 0  # аналог блокировки: 0 - не работает, 1 - работает
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
