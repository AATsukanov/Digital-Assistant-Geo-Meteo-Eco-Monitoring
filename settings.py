# Настройки окна
geometry = '652x472+0+0'
canvas_bg = '#AAA5B5'
canvas_bg_img = 'img/bg.png'

# Имя *.json файла для передачи параметров при запуске Telegram-бота:
fparams_json = f'params/exchange.$REPLACE=TODAY$.json'

# Путь сохранения временных статических карт:
temp_maps_folder = 'temp_maps/'

# zoom в веб-картах по-умолчанию:
maps_zoom = {'yandex-static': 14,
             'yandex': 15,
             'google': 15,
             'osm': 18,
             'nakarte': 17}

# Путь к Таблицам по-умолчанию:
tables_dir = 'tables/'
table_devices_info = 'tables/DevicesInfo.xlsx'
table_of_complects = 'tables/TableOfComplects.xlsx'

# настройки клавиатур telegram-бота:
points_PointID_kb_buttons_in_row: int = 4

# Сетка кнопок быстрого выбора комплекта приборов по GroupID (тип dict(int: list[int]):
devices_GroupID_kb_layout = {
                                1: [1],
                                2: [2],
                                3: [3],
                                4: [2, 2],
                                5: [2, 3],
                                6: [3, 3],
                                7: [2, 2, 3],
                                8: [2, 3, 3],
                                9: [3, 3, 3],
                                10: [2, 2, 3, 3],
                                11: [2, 3, 3, 3],
                                12: [3, 3, 3, 3],
                                13: [3, 3, 3, 4],
                                14: [3, 3, 4, 4],
                                15: [3, 4, 4, 4],
                                16: [4, 4, 4, 4]
                            }

# Поддерживаемые группы приборов (тип list[str]):
devices_groups = ['A', 'B', 'G', 'M', 'P', 'R', 'V', 'W', '1-99']

# Настройки размера выводимых списков точек и приборов в telegram-боте:
bot_max_show_complects: int = 32
bot_max_show_points: int = 20

# Файл с изображением прибора определенной группы:
def device_image(device_group: str) -> str:
    '''
    Возвращает путь к файлу с изображением прибора данной группы
    :param device_group: str - имя группы приборов (тип прибора)
    :return fname: str - путь к файлу с изображением
    '''
    fname = f'img/complect-{device_group}.png'
    return fname

# Язык по-умолчанию:
default_language = 'Ru'