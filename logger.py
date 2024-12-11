import logging
import sys
import datetime

logger = logging.getLogger(__name__)
filename_log = f'logs/log.{datetime.date.today()}.txt'  # каждый день в новый файл, если перезапускается

if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)
    # все в консоль от DEBUG:
    consol = logging.StreamHandler(stream=sys.stdout)
    consol.setLevel(logging.DEBUG)
    logger.addHandler(consol)
    # от INFO и выше в файл:
    file = logging.FileHandler(filename=filename_log, mode='a', encoding='utf-8')
    file.setLevel(logging.INFO)
    file.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s'))
    logger.addHandler(file)

    logger.set_handler = True

if __name__ == '__main__':
    # тестируем
    logger.debug('Тестовое сообщение DEBUG в log...')
    logger.info('Тестовое сообщение INFO в log...')
    logger.warning('Тестовое сообщение WARNING в log...')
    logger.error('Тестовое сообщение ERROR в log...')
    # print(3 / (2 - 2))

'''
logging.basicConfig(level=logging.INFO, filename=f'logs/log.{datetime.date.today()}.txt', filemode='a',
                    format='%(asctime)s\t%(levelname)s\t%(message)s', encoding='utf-8')
'''
