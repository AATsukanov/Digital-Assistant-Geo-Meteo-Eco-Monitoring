from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Открыть задание'),
            KeyboardButton(text='Свой профиль'),
        ],
        [
            KeyboardButton(text='Поддержка'),
            KeyboardButton(text='Информация')
        ],
        [
            KeyboardButton(text='Начать работу')
        ]
    ], resize_keyboard=True
)