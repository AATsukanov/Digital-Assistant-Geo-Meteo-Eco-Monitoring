import datetime

# Имя *.json файла для передачи параметров при запуске Telegram-бота:
fparams_json = f'params/exchange.{datetime.date.today()}.json'

# Путь сохранения временных статических карт:
temp_maps_folder = 'temp_maps/'

# Путь к Таблицам по-умолчанию:
tables_dir = 'tables/'
table_devices_info = 'tables/DevicesInfo.xlsx'
table_of_complects = 'tables/ComplectsTable.xlsx'

# Язык по-умолчанию:
default_language = 'Ru'

# Сетка кнопок быстрого выбора комплекта приборов по GroupID (тип dict(int: list(int)):
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

# Файл с изображением прибора определенной группы:
def device_image(device_group: str) -> str:
    '''
    Возвращает путь к файлу с изображением прибора данной группы
    :param device_group: str - имя группы приборов (тип прибора)
    :return fname: str - путь к файлу с изображением
    '''
    fname = f'img/complect-{device_group}.png'
    return fname