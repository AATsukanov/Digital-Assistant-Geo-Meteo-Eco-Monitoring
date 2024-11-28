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

admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Обновить свои данные из профиля', callback_data='update_admin')],
        [InlineKeyboardButton(text='Список специалистов', callback_data='show_users')],
        [InlineKeyboardButton(text='Список координаторов', callback_data='show_admins')],
        [InlineKeyboardButton(text='Статистика и прогресс', callback_data='users_stat')],
        [InlineKeyboardButton(text=' < назад', callback_data='back_admin_panel')]
    ]
)

activate_deactivate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Активир.', callback_data='activate_user'),
            InlineKeyboardButton(text='Деактив.', callback_data='deactivate_user')
        ],
        [InlineKeyboardButton(text=' < назад', callback_data='back_admin_panel')]
    ]
)

help_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Краткое руководство', callback_data='instruction')],
        [InlineKeyboardButton(text='Связь с разработчиком', callback_data='contact_me')],
        [InlineKeyboardButton(text='Контакты поддержки', callback_data='support_contacts')],
        #[InlineKeyboardButton(text=' < назад', callback_data='back_start_menu')]
    ]
)

def make_map_kb(lat: float, lon: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Яндекс карта', url=Earth.make_maps_yandex_url(lat, lon)),
                InlineKeyboardButton(text='Карта OSM', url=Earth.make_openstreetmap_url(lat, lon))
            ],
            [
                InlineKeyboardButton(text='Google map', url=Earth.make_maps_google_url(lat, lon)),
                InlineKeyboardButton(text='nakarte.me', url=Earth.make_maps_nakarte_url(lat, lon))
            ],
            #[InlineKeyboardButton(text=' < назад', callback_data='back_start_menu')]
        ]
    )
