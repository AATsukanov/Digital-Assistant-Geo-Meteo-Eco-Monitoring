# ставим python 3.9
# ставим aiogram 2.25.2

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import logging
import datetime

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
async def start(message):
    info = f'Специалист {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username}) подключился'
    logging.info(info)
    print(info)
    await message.answer(f'Здравствуйте, {message.from_user.username}!', reply_markup=kb.start_kb)

@dp.message_handler()
async def all_messages(message):
    await message.answer('Для начала, пожалуйста, нажмите на команду /start')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)