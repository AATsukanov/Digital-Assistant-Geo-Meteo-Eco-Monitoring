import tsukanoff  # Внимание: этот файл в gitignore, для работы настройте свой.
from dataclasses import dataclass

version = '0.0.1'
app_title = u'Цифровой Ассистент Системы Геомониторинга'
geometry = '640x480+0+0'
iconbitmap = 'icon.ico'

welcome_img = 'img/wpw.png'

token = tsukanoff.Telegram.token  # замените на Ваш Telegram-токен, например, token: str = 'AAААААААААААААААААААААА'
admins = [tsukanoff.Telegram.id, ]  # добавьте в список Telegram-id администраторов, например, id: int = 76543210

language_icon = 'img/Ru-Cn.png'

@dataclass
class AuthorInfo:
    author = 'Alexey A.Tsukanov'
    author_email = 'a.a.tsukanov@yandex.ru'
    author_page = 'scholar.google.com/citations?hl=en&user=4LlptA8AAAAJ'
    author_site = 'https://tsukanov-lab.moy.su/index/tsukanov_lab/0-2'