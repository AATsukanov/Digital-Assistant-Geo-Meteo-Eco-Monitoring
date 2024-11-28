# ставим python 3.9
# ставим aiogram 2.25.2

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
import asyncio
import datetime
import os
import sys
import json

# импорт своих модулей
import config
import keyboards as kb
import database as db
from datatypes import User, Admin
#import admin
import docs
from logger import logger

bot = Bot(token=config.token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

class AdminStates(StatesGroup):
    activate_user = State()
    deactivate_user = State()

async def on_startup(dispatcher: Dispatcher) -> None:
    await bot.set_my_commands([
        types.BotCommand('start', 'Запуск'),
        types.BotCommand('help',  'Помощь')
    ])

@dp.message_handler(commands=['start'])
async def start(message: Message):
    info = f'Специалист {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username}) подключился {message.date}'
    logger.info(info)
    # Проверяем пользователя в users.db и добавляем его открытые данные, если его нет:
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


@dp.callback_query_handler(text='back_start_menu')
async def back_start_menu(call: CallbackQuery):
    await call.message.answer('Меню:', reply_markup=kb.start_kb)
    await call.answer()


#@dp.message_handler(text=['Проверить своё позиционирование'])
@dp.message_handler(content_types = ['location'])
async def check_location(message: Message):
    lat, lon = message.location["latitude"], message.location["longitude"]
    logger.info(f'{message.date} Проверка геопозиции @{message.from_user.username} ({message.from_id}): {lat}, {lon}')
    await message.answer(text=f'Ваши координаты (LAT, LON): {lat}, {lon}', reply_markup=kb.make_map_kb(lat, lon))


@dp.message_handler(commands=['help'])
@dp.message_handler(text=['Поддержка'])
async def helper(message: Message):
    await message.answer(text='Помощь \ поддержка...', reply_markup=kb.help_kb)


@dp.callback_query_handler(text='instruction')
async def instruction(call: CallbackQuery):
    await call.message.answer(text=docs.instruction_ru,
                              parse_mode='html')
    await call.answer()


@dp.callback_query_handler(text='contact_me')
async def contact_me(call: CallbackQuery):
    await call.message.answer('По всем техническим вопросам можно обратиться к разработчику.\n'
                              'Напишите или позвоните мне через Telegram (в рабочее время по Москве):\n'
                              f'{config.my_contact}')
    await call.answer()


@dp.callback_query_handler(text='support_contacts')
async def support_contacts(call: CallbackQuery):
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
    await message.answer(text=msg, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['admin'])
async def admin(message: Message):
    if message.from_id in config.admins:
        await message.answer('Панель администратора', reply_markup=kb.admin_kb)
    else:
        await message.answer('Команда не распознана, для начала, пожалуйста, нажмите на /start')


@dp.callback_query_handler(text='back_admin_panel')
async def back_admin_panel(call: CallbackQuery):
    if call.from_user.id in config.admins:
        await call.message.answer('Панель управления', reply_markup=kb.admin_kb)
    else:
        await call.message.answer('Главное меню', reply_markup=kb.start_kb)
    await call.answer()


@dp.callback_query_handler(text='update_admin')
async def update_admin(call: CallbackQuery):
    a = Admin(id=call.from_user.id)
    print(type(call.from_user))
    a.update_from_tg(call.from_user)
    db.update_admin(a)
    await call.message.answer(text=f'<b>Обновлено</b>:\n{db.show_admin(admin_id=a.id)}',
                              parse_mode='html')
    await call.answer()


@dp.callback_query_handler(text='show_users')
async def show_users(call: CallbackQuery):
    text = f'<b>СПЕЦИАЛИСТЫ</b>\n\n{db.show_users()}'
    await call.message.answer(text=text,
                              parse_mode='html',
                              reply_markup=kb.activate_deactivate_kb)
    await call.answer()


@dp.callback_query_handler(text='show_admins')
async def show_admins(call: CallbackQuery):
    text = f'<b>КООРДИНАТОРЫ</b>\n\n{db.show_admins()}'
    await call.message.answer(text=text, parse_mode='html')
    await call.answer()


@dp.callback_query_handler(text='activate_user')
async def activate_user(call: CallbackQuery):
    await call.message.answer(text='Введите id пользователя для Активации:',
                              reply_markup=types.ReplyKeyboardRemove())
    await call.answer()
    await AdminStates.activate_user.set()


@dp.message_handler(state=AdminStates.activate_user)
async def activation(message: Message, state: State) -> None:
    text = message.text
    if text == '' or text == '/cancel' or not text.isdigit():
        await message.answer('Отменено...', reply_markup=kb.admin_kb)
        await state.finish()
        return
    user_id = int(text)
    if db.is_user_in_db(user_id):
        db.activate_user(user_id)
        user = db.get_user(user_id)
        msg = f'АКТИВИРОВАН аккаунт пользователя:\n{user[3]} {user[4]} @{user[5]}'
        await message.answer(text=msg, reply_markup=kb.admin_kb)
    else:
        await message.answer(text='Запись с таким id не найдена', reply_markup=kb.admin_kb)
    await state.finish()


@dp.callback_query_handler(text='deactivate_user')
async def deactivate_user(call: CallbackQuery):
    await call.message.answer(text='Введите id пользователя для Деактивации:',
                              reply_markup=types.ReplyKeyboardRemove())
    await call.answer()
    await AdminStates.deactivate_user.set()


@dp.message_handler(state=AdminStates.deactivate_user)
async def deactivation(message: Message, state: State) -> None:
    text = message.text
    if text == '' or text == '/cancel' or not text.isdigit():
        await message.answer('Отменено...', reply_markup=kb.admin_kb)
        await state.finish()
        return
    user_id = int(text)
    if db.is_user_in_db(user_id):
        db.deactivate_user(user_id)
        user = db.get_user(user_id)
        msg = f'ДЕАКТИВИРОВАН аккаунт пользователя:\n{user[3]} {user[4]} @{user[5]}'
        await message.answer(text=msg, reply_markup=kb.admin_kb)
    else:
        await message.answer(text='Запись с таким id не найдена', reply_markup=kb.admin_kb)
    await state.finish()


@dp.callback_query_handler(text='users_stat')
async def show_users_stat(call: CallbackQuery):
    n_users, n_admins, n_users_in_work, n_active_users = db.users_stat()
    text = '<b>Полевые специалисты</b>\n'
    text += f' - всего: {n_users}\n'
    text += f' - в работе: {n_users_in_work}\n'
    text += f' - активированных: {n_active_users}\n'
    text += f' - деактивированных: {n_users - n_active_users}\n\n'
    text += '<b>Координаторы</b>\n'
    text += f' - всего: {n_admins}'
    await call.message.answer(text=text, parse_mode='html')
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