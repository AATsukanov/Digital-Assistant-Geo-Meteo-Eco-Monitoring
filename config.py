import tsukanoff  # Внимание: этот файл в gitignore, для работы настройте свой.
from dataclasses import dataclass

version = '0.0.1'
app_title = u'Цифровой Ассистент Системы Геомониторинга'
iconbitmap = 'icon.ico'

welcome_img = 'img/wpwd.png'

token = tsukanoff.Telegram.token  # замените на Ваш Telegram-токен, например, token: str = 'AAААААААААААААААААААААА'
admins = [tsukanoff.Telegram.id,
          tsukanoff.Telegram.id2, ]  # добавьте в список Telegram-id администраторов, например, id: int = 76543210
my_contact = tsukanoff.Telegram.my_contact  # здесь я использую своё @username из telegram
language_icon = 'img/Ru-Cn.png'


@dataclass
class AuthorInfo:
    author: str = 'Alexey A.Tsukanov'
    author_phone: str = tsukanoff.phone_number  # номер телефона для поддержки
    author_email: str = 'a.a.tsukanov@yandex.ru'
    author_page: str = 'scholar.google.com/citations?hl=en&user=4LlptA8AAAAJ'
    author_site: str = 'https://tsukanov-lab.moy.su/index/tsukanov_lab/0-2'
