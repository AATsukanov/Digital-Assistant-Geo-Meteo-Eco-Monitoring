from dataclasses import dataclass
import aiogram.types as aiotypes

@dataclass
class User:
    id: int
    is_working_now: int = 0  # 0 -- не в поле, 10 -- начал работу, 100 -- завершил работу
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


