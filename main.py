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
import datetime
import os
import sys
import json

# импорт своих модулей
import config
import keyboards as kb
import database as db
from data_classes import User, Admin
#import admin
import helper
from logger import logger

bot = Bot(token=config.token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

async def on_startup(dispatcher: Dispatcher) -> None:
    await bot.set_my_commands([
        types.BotCommand('start', 'Запуск'),
        types.BotCommand('help',  'Помощь')
    ])

@dp.message_handler(commands=['start'])
async def start(message: Message):
    info = f'Специалист {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username}) подключился {message.date}'
    logger.info(info)
    # Проверяем пользователя в users.db и добавляем открытые данные, если его нет:
    greeting_name = 'уважаемый пользователь'
    if not db.is_user_in_db(message.from_id):
        user = User(message.from_id)
        user.fill_from_tg(message.from_user)
        db.add_user(user)
        if not user.first_name + user.last_name == '':
            greeting_name = user.first_name + ' ' + user.last_name
    else:
        greeting_name = db.get_greeting_name(user_id=message.from_id)
    with open(config.welcome_img, 'rb') as img:
        await message.answer_photo(photo=img, caption=f'Здравствуйте, {greeting_name}', reply_markup=kb.start_kb)



#@dp.message_handler(text=['Проверить своё позиционирование'])
@dp.message_handler(content_types = ['location'])
async def check_location(message: Message):
    lat, lon = message.location["latitude"], message.location["longitude"]
    logger.info(f'{message.date} Проверка геопозиции @{message.from_user.username} ({message.from_id}): {lat}, {lon}')
    await message.answer(text=f'Ваши координаты (LAT, LON): {lat}, {lon}', reply_markup=kb.make_map_kb(lat, lon))


@dp.message_handler(commands=['help'])
@dp.message_handler(text=['Поддержка'])
async def help(message: Message):
    await message.answer(text='Помощь \ поддержка...', reply_markup=kb.help_kb)


@dp.callback_query_handler(text='instruction')
async def instruction(call):
    await call.message.answer(text=helper.instruction_ru,
                              parse_mode='MarkdownV2')
    await call.answer()


@dp.callback_query_handler(text='contact_me')
async def contact_me(call):
    await call.message.answer(f'По всем техническим вопросам можно обратиться к разработчику.\nНапишите или позвоните мне через Telegram (в рабочее время по Москве): {config.my_contact}.')
    await call.answer()

@dp.callback_query_handler(text='support_contacts')
async def support_contacts(call):
    text = f'Разработчик: {config.AuthorInfo.author}\n'
    text += f'Телефон: <span class="tg-spoiler">{config.AuthorInfo.author_phone}</span>\n'
    text += f'e-mail: {config.AuthorInfo.author_email}\n'
    text += f'сайт автора: {config.AuthorInfo.author_site}\n'
    text += f'страница автора: {config.AuthorInfo.author_page}'
    await call.message.answer(text=text, parse_mode='html')
    await call.answer()


@dp.message_handler(commands=['end'])
async def end(message: Message):
    info = f'{message.date}: Специалист {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username}, {message.from_id}) нажал "/end"'
    logger.info(info)
    if db.user_completed_work(user_id=message.from_id):
        msg = 'Спасибо, Вы завершили работу!'
    else:
        msg = 'Невозможно завершить, работа не начата.'
    await message.answer(text=msg)  # await message.delete_reply_markup()

@dp.message_handler(commands=['admin'])
async def admin(message: Message):
    if message.from_id in config.admins:
        await message.answer('Панель администратора', reply_markup=kb.admin_kb)
    else:
        await message.answer('Команда не распознана, для начала, пожалуйста, нажмите на /start')

@dp.callback_query_handler(text='')
async def contact_me(call):
    await call.message.answer(f'По всем техническим вопросам можно обратиться к разработчику.\nНапишите или позвоните мне через Telegram (в рабочее время по Москве): {config.my_contact}.')
    await call.answer()

@dp.message_handler()
async def all_messages(message: Message):
    await message.answer('Команда не распознана, для начала, пожалуйста, нажмите на /start')


def main():
    for j, param in enumerate(sys.argv):
        print(f'{j}: sys.argv >> {param}')
    print('Количество аргументов:', len(sys.argv))

if __name__ == '__main__':
    main()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)