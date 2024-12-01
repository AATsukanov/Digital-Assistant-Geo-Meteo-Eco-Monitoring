import json

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import settings
from earth import Earth
from settings import devices_GroupID_kb_layout, max_kb_buttons_in_row

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Открыть задание'),
            KeyboardButton(text='Свой профиль'),
        ],
        [
            KeyboardButton(text='Проверить свою геолокацию', request_location=True,)
        ],
        [
            KeyboardButton(text='Поддержка'),
            KeyboardButton(text='Приборная база')
        ],
        [
            KeyboardButton(text='Начать работу >')
        ]
    ], resize_keyboard=True
)

admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Обновить свои данные из профиля', callback_data='update_admin')],
        [InlineKeyboardButton(text='Список специалистов', callback_data='show_users')],
        [InlineKeyboardButton(text='Список координаторов', callback_data='show_admins')],
        [InlineKeyboardButton(text='Статистика и прогресс', callback_data='users_stat')]
    ], resize_keyboard=True
)

activate_deactivate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Активир.', callback_data='activate_user'),
            InlineKeyboardButton(text='Деактив.', callback_data='deactivate_user')
        ],
        [InlineKeyboardButton(text=' < назад', callback_data='back_admin_panel')]
    ], resize_keyboard=True
)


user_profile_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Подгрузить из tg-профиля', callback_data='update_user_from_telegram')],
        [InlineKeyboardButton(text='Заполнить данные вручную', callback_data='update_user_by_user')],
    ], resize_keyboard=True
)


help_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Краткое руководство', callback_data='instruction')],
        [InlineKeyboardButton(text='Связь с разработчиком', callback_data='contact_me')],
        [InlineKeyboardButton(text='Контакты поддержки', callback_data='support_contacts')]
    ], resize_keyboard=True
)


def all_groups_kb() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup(resize_keyboard=True)
    for gid in settings.devices_groups:
        inline_kb.insert(InlineKeyboardButton(text=f'{gid}',
                                              callback_data=json.dumps({'#': 'Groups', 'GroupID': gid})))
    return inline_kb


def groups_kb(groups_list: list[str]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for gid in groups_list:
        kb.insert(KeyboardButton(text=gid))
    return kb


def subgroups_kb(subgroups_list: list[str]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for sub in subgroups_list:
        kb.insert(KeyboardButton(text=sub))
    return kb


def complects_new_kb(complects_list: list[str]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for cid in list(complects_list):
        row.append(KeyboardButton(text=cid))
        if len(row) % max_kb_buttons_in_row == 0:
            kb.row(row)
            row = []
    # оставшиеся:
    if len(row) > 0:
        kb.row(row)
    return kb


def complects_kb(complects_list: list[str]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for cid in complects_list:
        kb.insert(KeyboardButton(text=cid))
    return kb


def points_kb(points_list: list[str]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for pid in points_list:
        kb.insert(KeyboardButton(text=pid))
    return kb

def points_adpt_kb(points_list: list[str]) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for pid in points_list:
        row.append(KeyboardButton(text=pid))
        if len(row) % max_kb_buttons_in_row == 0:
            kb.row(row)
            row = []
    # оставшиеся:
    if len(row) > 0:
        kb.row(row)
    return kb


def url_kb(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='перейти на сайт производителя', url=url)]],
                                resize_keyboard=True)


def make_map_kb(lat: float, lon: float, reg_loc_button: dict) -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardMarkup()
    b11 = InlineKeyboardButton(text='Яндекс карта',
                               url=Earth.make_maps_yandex_url(lat, lon, settings.maps_zoom['yandex']))
    b12 = InlineKeyboardButton(text='Карта OSM',
                               url=Earth.make_openstreetmap_url(lat, lon, settings.maps_zoom['osm']))
    b21 = InlineKeyboardButton(text='Google map',
                               url=Earth.make_maps_google_url(lat, lon, settings.maps_zoom['google']))
    b22 = InlineKeyboardButton(text='nakarte.me',
                               url=Earth.make_maps_nakarte_url(lat, lon, settings.maps_zoom['nakarte']))
    inline_kb.row(b11, b12)
    inline_kb.row(b21, b22)
    if reg_loc_button['visible']:
        b3 = InlineKeyboardButton(text=reg_loc_button['label'],
                                  callback_data=json.dumps({'#': 'Setup', 'lat': lat, 'lon': lon}))
        inline_kb.row(b3)
    return inline_kb

field_info_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Проектные точки (актуальные)', callback_data='project_points_rest')],
        [InlineKeyboardButton(text='Комплекты приборов (свободные)', callback_data='project_devices_free')],
        [InlineKeyboardButton(text='Проектные точки (с приборами)', callback_data='project_points_started')],
        [InlineKeyboardButton(text='Комплекты приборов (на точках)', callback_data='project_devices_busy')],
        [InlineKeyboardButton(text='Полевой отряд (кто с Вами в поле)', callback_data='users_in_the_field')]
    ], resize_keyboard=True
)

work_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Текущий прогресс')],
        [KeyboardButton(text='Установить прибор (запрос геолокации)', request_location=True)],
        [
            KeyboardButton(text='< в главное меню'), KeyboardButton(text='Снять прибор')
        ]
    ], resize_keyboard=True
)


