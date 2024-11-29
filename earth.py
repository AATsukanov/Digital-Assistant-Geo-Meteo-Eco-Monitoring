import requests as rq
import os

import settings

class MyStaticMaps(object):
    # простая работа с растровыми картами:
    # https://yandex.ru/dev/staticapi/doc/ru/request/markers
    def __init__(self):
        # создаем папку для временных png-файлов:
        if not os.path.isdir(settings.temp_maps_folder):
            os.mkdir(settings.temp_maps_folder)
        self.workdir = settings.temp_maps_folder
        # Параметры со значениями по-умолчанию:
        self.fname: str = ''
        self.mode: str = 'AUTO'  # возможны 'SPAN', 'AUTO', 'ZOOM'
        self.cLon: float = 42.442
        self.cLat: float = 43.355  # Координаты центра карты на старте (Эльбрус, например)
        self.zoom: int = 14  # Масштаб карты на старте. Изменяется от 1 до 17
        self.type = 'map'  # &l=map&, другие значения 'map', 'sat', 'sat,skl'
        self.spn_x = 2.5  # в градусах для режима SPAN
        self.spn_y = 2.5  # размер поля
        self.size_x = 650  # max 650x450
        self.size_y = 450
        self.lang = 'ru_RU'  # 'en_RU'
        self.current_map_request = ''
        self.xPointsLon: list[float] = []
        self.yPointsLat: list[float] = []
        self.PointsStatus: list[str] = []  # 'Я' -- значок своего положения, 'Т' -- точка, 'П' -- точка с прибором
        self.MAX_N_POINTS: int = 99  # ограничение static карт

    def copy_points(self, longitude: list[float], latitude: list[float], status: list[str]):
        self.xPointsLon = longitude.copy()
        self.yPointsLat = latitude.copy()
        self.PointsStatus = status.copy()

    def _make_request(self):
        nPoints = len(self.xPointsLon)
        if nPoints > 0:
            # Режим AUTO доступен только в случае наличия точек-меток
            self.mode = 'AUTO'
        else:
            self.mode = 'SPAN'
        # собираем запрос (см. https://yandex.ru/dev/staticapi/doc/ru/):
        URL = 'https://static-maps.yandex.ru/1.x/?'
        URL += f'l={self.type}&'
        URL += f'size={self.size_x},{self.size_y}&'
        if self.mode != 'AUTO':
            URL += f'll={self.cLon},{self.cLat}&'
        if self.mode == 'SPAN':
            URL += f'spn={self.spn_x},{self.spn_y}&'
        if self.mode == 'ZOOM':
            URL += f'z={self.zoom}&'
        if self.lang != 'ru_RU':
            URL += f'lang={self.lang}&'

        if nPoints > 0:
            URL += 'pt='
            for j in range(nPoints):
                if j >= self.MAX_N_POINTS:
                    print(u'ВНИМАНИЕ: Превышено максимальное количество точек-меток 99.')
                    break
                x = self.xPointsLon[j]
                y = self.yPointsLat[j]
                if self.PointsStatus[j] == 'Я':
                    style = 'ya_ru'
                    color = ''
                    size = ''
                    content = ''
                elif self.PointsStatus[j] == 'Т':
                    style = 'vk'
                    color = 'bk'
                    size = 'm'
                    content = ''
                elif self.PointsStatus[j] == 'П':
                    style = 'vk'
                    color = 'gr'
                    size = 'm'
                    content = ''
                else:
                    style = 'round'
                    color = ''
                    size = ''
                    content = ''
                URL += f'{x:.6f},{y:.6f},{style}{color}{size}{content}' + '~'
            # теперь убираем лишнюю тильду в конце:
            URL = URL[:-1]

        self.current_map_request = URL
        return self.current_map_request

    def _make_fname(self):
        fname = f'_temp_yandex_{self.mode}_'
        if self.mode != 'AUTO':
            fname += f'{self.cLon}-{self.cLat}_'
        if self.mode == 'SPAN':
            fname += f'spn={self.spn_x}-{self.spn_y}_'
        if self.mode == 'ZOOM':
            fname += f'{self.zoom}_'
        fname += f'n={len(self.xPointsLon)}.png'
        return os.path.join(self.workdir, fname)

    def load_map(self) -> str:
        '''При успешном завершении запроса функция возвращает str
        имя временного png-файла со статической картой.
        '''
        # создаем строку запроса:
        self._make_request()  # результат записывается в переменную self.current_map_request
        if self.current_map_request == '':
            return ''
        response = rq.get(self.current_map_request)
        if not response:
            print(u'ОШИБКА: Ошибка выполнения запроса:')
            print(self.current_map_request)
            print(f'http статус: {response.status_code} ({response.reason})')
            print(f'Содержание отклика: {response.content})')
            return ''
        # Запись полученного изображения в файл:
        self.fname = self._make_fname()
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
    def make_maps_google_url(lat: float, lon: float, zoom: int = 14) -> str:
        url = f'https://www.google.com/maps/@{lat},{lon},{zoom}z'
        return url

    @staticmethod
    def make_maps_nakarte_url(lat: float, lon: float, zoom: int = 14) -> str:
        url = f'https://nakarte.me/#m={zoom}/{lat}/{lon}&l=O'
        return url