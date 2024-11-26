from dataclasses import dataclass

@dataclass
class User:
    id: int
    first_name: str = '(пусто)'
    last_name: str = '(пусто)'
    username: str = '(пусто)'
    language_code: str = '(пусто)'
    phone: str = '(пусто)'
    country: str = '(пусто)'
    city: str = '(пусто)'
    birthdate: str = 'ГГГГ-ММ-ДД'
    work_email: str = '(пусто)'

@dataclass
class Admin:
    id: int
    first_name: str = '(пусто)'
    last_name: str = '(пусто)'
    username: str = '(пусто)'
    language_code: str = 'ru'

user_changeable_columns = ['phone', 'country', 'city', 'birthdate', 'work_email']