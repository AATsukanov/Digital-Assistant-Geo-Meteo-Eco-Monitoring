import json
from dataclasses import dataclass

@dataclass
class User:
    id: int
    is_working_now: int = 0  # 0 -- не в поле, 10 -- начал работу, 100 -- завершил работу
    is_active: int = 1  # аналог блокировки
    first_name: str = ''
    last_name: str = ''
    username: str = '(не указан)'
    language_code: str = 'ru'
    phone: str = '(пусто)'
    country: str = '(пусто)'
    city: str = '(пусто)'
    birthdate: str = 'ГГГГ-ММ-ДД'
    work_email: str = '(пусто)'

    def fill_from_tg(self, user_tg, echo: bool=False):
        user = dict(user_tg)
        if echo:
            print(f'Заполняем пользователя из user_json = {user}')
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

    def fill_from_json(self, admin_json):
        self.id = admin_json['id']
        self.first_name = admin_json['first_name']
        self.last_name = admin_json['last_name']
        self.username = admin_json['username']
        self.language_code = admin_json['language_code']

user_changeable_columns = ['first_name', 'last_name', 'phone', 'country', 'city', 'birthdate', 'work_email']