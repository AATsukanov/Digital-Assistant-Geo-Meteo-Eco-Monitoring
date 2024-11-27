

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