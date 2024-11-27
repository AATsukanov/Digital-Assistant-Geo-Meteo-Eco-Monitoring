from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from my_earth import Earth

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Открыть задание'),
            KeyboardButton(text='Свой профиль'),
        ],
        [
            KeyboardButton(text='Проверить свою геолокацию', request_location=True, )
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

help_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Краткое руководство', callback_data='instruction')],
        [InlineKeyboardButton(text='Связь с разработчиком', callback_data='contact')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_start_kb')]
    ]
)

def make_map_kb(lat: float, lon: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='На Яндекс карту', url=Earth.make_maps_yandex_url(lat, lon))],
            [InlineKeyboardButton(text='На OSM карту', url=Earth.make_openstreetmap_url(lat, lon))],
            [InlineKeyboardButton(text='На карту Google', url=Earth.make_maps_google_url(lat, lon))],
            [InlineKeyboardButton(text='На nakarte.me', url=Earth.make_maps_nakarte_url(lat, lon))]
        ]
    )
