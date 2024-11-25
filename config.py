import tsukanoff

app_title = u'Цифровой Ассистент Системы Геомониторинга'
geometry = '640x480'

token = tsukanoff.Telegram.token  # замените на Ваш Telegram-токен, например, token: str = 'AAААААААААААААААААААААА'
admins = [tsukanoff.Telegram.id, ]  # добавьте в список Telegram-id администраторов, например, id: int = 76543210