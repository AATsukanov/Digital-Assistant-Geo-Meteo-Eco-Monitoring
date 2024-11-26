# ставим python 3.9
# ставим aiogram 2.25.2

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
import asyncio
import logging
import datetime
import os
import sys
import json

# импорт своих модулей
import config
import keyboards as kb
#import admin
import database as db
#import texts

logging.basicConfig(level=logging.INFO, filename=f'logs/log.{datetime.date.today()}.txt', filemode='a',
                    format='%(asctime)s\t%(levelname)s\t%(message)s', encoding='utf-8')

bot = Bot(token=config.token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start(message: Message):
    info = f'Специалист {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username}) подключился'
    logging.info(info)
    print(info)
    with open(config.welcome_img, 'rb') as img:
        await message.answer_photo(photo=img, caption=f'Здравствуйте, {message.from_user.username}!', reply_markup=kb.start_kb)
    # Проверяем пользователя в users.db и добавляем открытые данные, если его нет:
    print(message.location)
    print(message.from_user.as_json())
    #if not db.check_user_in_db(message.from_user.id):
    #    db.add_user()

@dp.message_handler(text=['Проверить свои координаты'])
async def check_location(message: Message):
    print(message.location.as_json())
    #await message.answer(text=f'Ваши координаты: {message.location}')

@dp.message_handler(commands=['end'])
async def end(message: Message):
    info = f'Специалист {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username}) нажал "/end"'
    logging.info(info)
    print(info)
    await message.answer(reply_markup=None)


@dp.message_handler()
async def all_messages(message: Message):
    await message.answer('Для начала, пожалуйста, нажмите на команду /start')

def main():
    for j, param in enumerate(sys.argv):
        print(f'{j}: sys.argv >> {param}')
    print('Количество аргументов:', len(sys.argv))

if __name__ == '__main__':
    main()
    executor.start_polling(dp, skip_updates=True)