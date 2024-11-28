import requests as rq
import os

import settings

class MyStaticMaps(object):
    # простая работа с растровыми картами:
    def __init__(self):
        # создаем папку для временных png-файлов:
        if not os.path.isdir(settings.temp_maps_folder):
            os.mkdir(settings.temp_maps_folder)
        self.workdir = settings.temp_maps_folder
        # Параметры со значениями по-умолчанию:
        self.fname: str = ''
        self.mode: str = 'AUTO'  # возможны 'SPAN', 'AUTO', 'ZOOM'
        self.lon: float = 39.740277
        self.lat: float = 43.568913  # Координаты центра карты на старте (Сочи, например!)
        self.zoom: int = 14  # Масштаб карты на старте. Изменяется от 1 до 17
        self.type = 'map'  # &l=map&, другие значения 'map', 'sat', 'sat,skl'
        self.spn_x = 2.5
        self.spn_y = 2.5
        self.size_x = 650  # max 650x450
        self.size_y = 450
        self.lang = 'ru_RU'  # 'en_RU'
        self.current_map_request = ''
        self.xPointsLon: list[float] = []
        self.yPointsLat: list[float] = []
        # {долгота},{широта},{стиль}{цвет}{размер}{контент}
        self.style = 'vk'  # pm, pm2, flag, vk
        self.color_all = 'bk'
        self.color_1st = 'gr'
        self.size: str = 'm'
        self.content: str = ''
        self.MAX_N_POINTS: int = 99  # ограничение static карт

    def copy_points(self, LON, LAT):
        self.xPointsLon = LON.copy()
        self.yPointsLat = LAT.copy()

    def make_request(self):
        if len(self.xPointsLon) * len(self.yPointsLat) == 0:
        if self.mode == 'AUTO':

                print(u'ОШИБКА: Режим AUTO доступен только в случае наличия точек-меток!')
                self.current_map_request = ''
                return ''
        URL = 'https://static-maps.yandex.ru/1.x/?'
        URL += f'l={self.type}&'
        URL += f'size={self.size_x},{self.size_y}&'
        if self.mode != 'AUTO':
            URL += f'll={self.lon},{self.lat}&'
        if self.mode == 'SPAN':
            URL += f'spn={self.spn_x},{self.spn_y}&'
        if self.mode == 'ZOOM':
            URL += f'z={self.zoom}&'
        if self.lang != 'ru_RU':
            URL += f'lang={self.lang}&'
        if len(self.xPointsLon) * len(self.yPointsLat) > 0:
            URL += 'pt='
            for j in range(1, len(self.xPointsLon)):
                if j >= self.MAX_N_POINTS:
                    print(u'ВНИМАНИЕ/ВАЖНО: Превышено максимальное количество точек-меток 99.')
                    break
                x = self.xPointsLon[j]
                y = self.yPointsLat[j]
                color = self.color_all
                URL += f'{x:.6f},{y:.6f},{self.style}{color}{self.size}{self.content}' + '~'
            # первую точку поверх всех:
            x = self.xPointsLon[0]
            y = self.yPointsLat[0]
            color = self.color_1st
            URL += f'{x},{y},{self.style}{color}{self.size}{self.content}'
        self.current_map_request = URL
        return self.current_map_request

    def make_fname(self):
        fname = f'_temp_yandex_{self.mode}_{self.lon}_{self.lat}'
        fname += f'_{self.spn_x}_{self.spn_y}_{self.zoom}_n{len(self.xPointsLon)}.png'
        return fname

    def load_map(self) -> str:
        # создаем строку запроса:
        self.make_request()
        if self.current_map_request == '':
            return ''
        # (результат записывается в переменную self.current_map_request)
        response = rq.get(self.current_map_request)
        if not response:
            print(u'ОШИБКА: Ошибка выполнения запроса:')
            print(self.current_map_request)
            print(f'http статус: {response.status_code} ({response.reason})')
            print(f'Содержание отклика: {response.content})')
            return ''
        # Запись полученного изображения в файл:
        self.fname = self.workdir + '/' + self.make_fname()
        try:
            with open(self.fname, "wb") as file:
                file.write(response.content)
        except IOError as exc:
            print('ОШИБКА: Ошибка записи временного файла:', exc)
            return ''
        return self.fname


class Earth:

    @staticmethod
    def make_maps_yandex_url(lat: float, lon: float, zoom: int=14) -> str:
        url = f'https://yandex.ru/maps/?ll={lon}%2C{lat}&z={zoom}'
        return url

    @staticmethod
    def make_openstreetmap_url(lat: float, lon: float, zoom: int=14) -> str:
        url = f'https://www.openstreetmap.org/#map={zoom}/{lat}/{lon}'
        return url

    @staticmethod
    def make_maps_google_url(lat: float, lon: float, zoom: int = 12) -> str:
        url = f'https://www.google.com/maps/@{lat},{lon},{zoom}z'
        return url

    @staticmethod
    def make_maps_nakarte_url(lat: float, lon: float, zoom: int = 12) -> str:
        url = f'https://nakarte.me/#m={zoom}/{lat}/{lon}&l=O'
        return url