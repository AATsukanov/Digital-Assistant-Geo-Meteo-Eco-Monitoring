import pandas as pd
import settings
import config


def get_devices_description(GroupID: str) -> tuple[str, str, str]:
    """Возвращает информацию о типах устройств из приборной базы"""
    # вначале заполним по-умолчанию из предположения, что возникла ошибка:
    DeviceModel = 'Модель не найдена'
    Description = 'Описание прибора не удалось получить. Пожалуйста, сообщите об ошибке разработчику'
    url = f'mailto:{config.AuthorInfo.author_email}'

    try:
        df = pd.read_excel(settings.table_devices_info)
    except Exception as exc:
        print('ОШИБКА: проблема при попытки открытия файла '
              f'{settings.table_devices_info} с помощью pd.read_excel:\n{exc}')
        return DeviceModel, Description, url

    # выбираем только строку с нужным GroupID:
    df = df[df['GroupID'] == GroupID]

    DeviceModel = list(df['DeviceModel'])[0]
    Description = list(df['Description'])[0]
    url = list(df['URL'])[0]

    return DeviceModel, Description, url


if __name__ == '__main__':
    for j, gid in enumerate(settings.devices_groups):
        dm, desc, url = get_devices_description(gid)
        print(f'{j}:\t{gid}\t{dm}\t{desc}\t{url}')
