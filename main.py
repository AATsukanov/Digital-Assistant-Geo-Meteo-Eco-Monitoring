from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
#from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
#import asyncio
import sys
import json

# импорт своих модулей
import config
import settings
import datatypes
import keyboards as kb
import database as db
from datatypes import User, Admin
import docs
import utils
from logger import logger

bot = Bot(token=config.token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

input_data: dict = {}  # параметры задания и другие входные данные (json) от основного приложения (app)
# динамическая настройка видимости кнопки регистрации геолокации точки:
reg_loc_button: dict = {(0, 'visible'): False, (0, 'label'): ''}


class WorkStates(StatesGroup):
    point_id = State()
    group_id = State()
    subgroup = State()
    complect = State()


class EndStates(StatesGroup):
    pickup_point_id = State()


class UserStates(StatesGroup):
    update_user_param = State()


class AdminStates(StatesGroup):
    activate_user = State()
    deactivate_user = State()


async def on_startup(dispatcher: Dispatcher) -> None:
    await bot.set_my_commands([
        types.BotCommand('start', 'ЗАПУСК'),
        types.BotCommand('menu', 'Главное меню'),
        types.BotCommand('rm', 'Очистить клавиатуру'),
        types.BotCommand('help',  'Помощь'),
        types.BotCommand('end', 'Завершить')
    ])


@dp.message_handler(commands=['start'])
async def start(message: Message):
    info = f'Специалист {message.from_user.first_name} {message.from_user.last_name} '\
           f'(@{message.from_user.username}) подключился {message.date}'
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
    global reg_loc_button
    reg_loc_button[(message.from_id, 'visible')] = False  # для start_kb reg_loc_button - invisible
    with open(config.welcome_img, 'rb') as img:
        await message.answer_photo(photo=img, caption=f'Здравствуйте, {greeting_name}', reply_markup=kb.start_kb)


@dp.message_handler(commands=['menu'])
@dp.message_handler(text=['< в главное меню'])
async def back_start_menu(message: Message):
    global reg_loc_button
    # для start_kb reg_loc_button - invisible:
    reg_loc_button[(message.from_id, 'visible')] = False
    await message.answer('Клавиатура начального меню:', reply_markup=kb.start_kb)


@dp.callback_query_handler(text='back_user_profile')
async def back_user_profile(call: CallbackQuery):
    await call.message.answer('Меню пользователя:', reply_markup=kb.user_profile_kb)
    await call.answer()


@dp.message_handler(content_types=['location'])
async def check_location(message: Message):
    global reg_loc_button
    if db.user_started_work(message.from_id) == 0:
        reg_loc_button[(message.from_id, 'visible')] = False
    lat, lon = message.location['latitude'], message.location['longitude']
    logger.info(f'{message.date} Проверка геопозиции @{message.from_user.username} ({message.from_id}): {lat}, {lon}')
    visible = reg_loc_button.get((message.from_id, 'visible'), False)
    label = reg_loc_button.get((message.from_id, 'label'), '')
    await message.answer(text=f'Ваши координаты (LAT, LON): {lat}, {lon}',
                         reply_markup=kb.make_map_kb(lat, lon,
                                                     reg_loc_button_visible=visible,
                                                     reg_loc_button_label=label))


@dp.message_handler(text='Свой профиль')
async def user_profile(message: Message):
    if db.user_is_active(message.from_id) == 0:
        await message.answer(text='Ваш профиль пока не активирован, обратитесь в поддержку.')
        return
    msg = '<b>Мой профиль</b>\n\n'
    for column_name, value in zip(datatypes.user_all_columns, db.get_user(message.from_id)):
        msg += f'<b>{column_name}</b>:\t{value}\n'
    await message.answer(text=msg, parse_mode='html', reply_markup=kb.user_profile_kb)


@dp.callback_query_handler(text='update_user_from_telegram')
async def update_user_from_telegram(call: CallbackQuery):
    db.update_user_from_tg(call.from_user)
    await call.message.answer('Обновлено из telegram-профиля', reply_markup=kb.user_profile_kb)
    await call.answer()


@dp.callback_query_handler(text='update_user_by_user')
async def update_user_by_user(call: CallbackQuery):
    await call.message.answer('Введите имя поля и его значение через пробел, например:\n'
                              'last_name Менделеев')
    await call.answer()
    await UserStates.update_user_param.set()


@dp.message_handler(state=UserStates.update_user_param)
async def update_user_param(message: Message, state) -> None:
    text = message.text
    if len(text.split(' ')) != 2:
        await message.answer('Неверный формат', reply_markup=kb.user_profile_kb)
        await state.finish()
        return
    column_name, value = text.split(' ')
    column_name = column_name.lower()
    uspex = db.update_user(message.from_id, column_name=column_name, value=value)
    if uspex:
        await message.answer(text=f'В поле "{column_name}" записано "{value}"', reply_markup=kb.user_profile_kb)
    else:
        await message.answer(text='Операция не выполнена, проверьте, пожалуйста, введенные данные.',
                             reply_markup=kb.user_profile_kb)
    await state.finish()


@dp.message_handler(commands=['help'])
@dp.message_handler(text=['Поддержка'])
async def helper(message: Message):
    await message.answer(text='Помощь / поддержка', reply_markup=kb.help_kb)


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


@dp.message_handler(text='Открыть задание')
async def open_task(message: Message):
    global input_data
    global reg_loc_button  # для start_kb reg_loc_button - invisible:
    reg_loc_button[(message.from_id, 'visible')] = False
    if db.user_is_active(message.from_id) == 0:
        await message.answer(text='Ваш профиль пока не активирован, обратитесь в поддержку.')
        return
    if input_data == {}:
        await message.answer(text='Текущие задания отсутствуют', reply_markup=kb.start_kb)
    # направляем схему точек и меню
    with open(input_data['map_image'], 'rb') as map_image:
        await message.answer_photo(photo=map_image,
                                   caption=f'<b>{input_data["ProjectName"]}</b>\n{input_data["TaskDetails"]}',
                                   parse_mode='html',
                                   reply_markup=kb.start_kb)


@dp.message_handler(text='Приборная база')
async def devices_base(message: Message):
    if db.user_is_active(message.from_id) == 0:
        await message.answer(text='Ваш профиль пока не активирован, обратитесь в поддержку.')
        return
    await message.answer('Выберите тип прибора по GroupID:', reply_markup=kb.all_groups_kb())


@dp.message_handler(text='Начать работу >')
async def start_work(message: Message):
    if db.user_is_active(message.from_id) == 0:
        await message.answer(text='Ваш профиль пока не активирован, обратитесь в поддержку.')
        return
    db.user_started_work(message.from_id)
    global reg_loc_button
    reg_loc_button[(message.from_id, 'visible')] = True
    reg_loc_button[(message.from_id, 'label')] = 'Зарегистрировать точку'
    await message.answer(text='Приступить к полевым работам', reply_markup=kb.work_menu_kb)


@dp.message_handler(text='Текущий прогресс')
async def current_progress_info(message: Message):
    if db.user_started_work(message.from_id) == 0:
        await message.answer(text='Сначала, пожалуйста, нажмите "Начать работу".')
        return
    await message.answer(text='Текущий прогресс:', reply_markup=kb.field_info_kb)


@dp.callback_query_handler(text='project_points_rest')
async def project_points_rest(call: CallbackQuery):
    text = db.get_points_rest()
    if text == '':
        text = 'в текущем задании не осталось точек для постановки'
    await call.message.answer(text=f'<b>Оставшиеся точки для постановки:</b>\n\n{text}',
                              parse_mode='html', reply_markup=kb.field_info_kb)
    await call.answer()


@dp.callback_query_handler(text='project_points_started')
async def project_points_started(call: CallbackQuery):
    text = db.get_points_started()
    if text == '':
        text = 'нет точек с установленным оборудованием'
    await call.message.answer(text=f'<b>Проектные точки с приборами:</b>\n\n{text}',
                              parse_mode='html', reply_markup=kb.field_info_kb)
    await call.answer()


@dp.callback_query_handler(text='project_devices_free')
async def project_devices_free(call: CallbackQuery):
    text = db.get_free_complects()
    await call.message.answer(text=f'<b>Свободные комплекты:</b>\n\n{text}',
                              parse_mode='html', reply_markup=kb.field_info_kb)
    await call.answer()


@dp.callback_query_handler(text='project_devices_busy')
async def project_devices_busy(call: CallbackQuery):
    text = db.get_busy_complects()
    await call.message.answer(text=f'<b>Установленные комплекты:</b>\n\n{text}',
                              parse_mode='html', reply_markup=kb.field_info_kb)
    await call.answer()


@dp.callback_query_handler(text='users_in_the_field')
async def users_in_the_field(call: CallbackQuery):
    text = db.get_users_in_the_field()
    if text == '':
        text = 'никто не отметился...'
    await call.message.answer(text=f'<b>Полевой отряд:</b>\n\n{text}',
                              parse_mode='html', reply_markup=kb.field_info_kb)
    await call.answer()


@dp.message_handler(commands=['end'])
async def end(message: Message):
    global reg_loc_button
    reg_loc_button[(message.from_id, 'visible')] = False
    info = f'{message.date}: Специалист {message.from_user.first_name} {message.from_user.last_name} '\
           f'(@{message.from_user.username}, {message.from_id}) нажал "/end"'
    logger.info(info)
    if db.user_completed_work(user_id=message.from_id):
        msg = 'Спасибо, Вы завершили работу!'
    else:
        msg = 'Невозможно завершить, работа не начата.'
    await message.answer(text=msg, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['rm'])
async def rm_command(message: types.Message):
    global reg_loc_button
    reg_loc_button[(message.from_id, 'visible')] = False
    await message.reply(r'очистить клавиатуру /rm', reply_markup=types.ReplyKeyboardRemove())


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
        global reg_loc_button
        reg_loc_button[(call.message.from_id, 'visible')] = False
        await call.message.answer('Главное меню', reply_markup=kb.start_kb)
    await call.answer()


@dp.callback_query_handler(text='update_admin')
async def update_admin(call: CallbackQuery):
    a = Admin(id=call.from_user.id)
    a.update_from_tg(call.from_user)
    db.update_admin(a)
    await call.message.answer(text=f'<b>Обновлено</b>:\n{db.get_admin(admin_id=a.id)}',
                              parse_mode='html')
    await call.answer()


@dp.callback_query_handler(text='show_users')
async def show_users(call: CallbackQuery):
    text = f'<b>СПЕЦИАЛИСТЫ</b>\n\n{db.get_users()}'
    await call.message.answer(text=text,
                              parse_mode='html',
                              reply_markup=kb.activate_deactivate_kb)
    await call.answer()


@dp.callback_query_handler(text='show_admins')
async def show_admins(call: CallbackQuery):
    text = f'<b>КООРДИНАТОРЫ</b>\n\n{db.get_admins()}'
    await call.message.answer(text=text, parse_mode='html')
    await call.answer()


@dp.callback_query_handler(text='activate_user')
async def activate_user(call: CallbackQuery):
    await call.message.answer(text='Введите id пользователя для Активации:',
                              reply_markup=types.ReplyKeyboardRemove())
    await call.answer()
    await AdminStates.activate_user.set()


@dp.message_handler(state=AdminStates.activate_user)
async def activation(message: Message, state) -> None:
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
async def deactivation(message: Message, state) -> None:
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
async def show_users_stat(call: CallbackQuery) -> None:
    n_users, n_admins, n_users_in_work, n_active_users = db.users_stat()
    text = '<b>ПОЛЕВЫЕ СПЕЦИАЛИСТЫ</b>\n'
    text += f' - всего: {n_users}\n'
    text += f' - в работе: {n_users_in_work}\n'
    text += f' - активированных: {n_active_users}\n'
    text += f' - деактивированных: {n_users - n_active_users}\n\n'
    text += '<b>КООРДИНАТОРЫ</b>\n'
    text += f' - всего: {n_admins}'
    await call.message.answer(text=text, parse_mode='html')
    await call.answer()


@dp.callback_query_handler(lambda callback_query: json.loads(callback_query.data)['#'] == 'Setup')
async def point_coordinates(call: CallbackQuery) -> None:
    global input_data
    callback_data = call.data
    callback_data = json.loads(callback_data)
    lat = callback_data['lat']
    lon = callback_data['lon']
    input_data[f'{call.from_user.id}']: list[float] = [lat, lon]
    await call.message.answer(text=f'Координаты постановки <b>{lat}, {lon}</b> - зарегистрированы!', parse_mode='html')
    await call.message.answer(text='<b>Выберите имя точки установки:</b>', parse_mode='html',
                              reply_markup=kb.points_kb(input_data['Point_ID']))
    await call.answer()
    await WorkStates.point_id.set()


@dp.message_handler(state=WorkStates.point_id)
async def set_point_id(message: Message, state) -> None:
    global input_data
    await state.update_data(point_id=message.text)
    groups_list = list(input_data['subgroups_dict'])
    await message.answer(text='<b>Выберите группу приборов</b> Group ID:', parse_mode='html',
                         reply_markup=kb.groups_kb(groups_list))
    await WorkStates.group_id.set()


@dp.message_handler(state=WorkStates.group_id)
async def set_group_id(message: Message, state) -> None:
    global input_data
    await state.update_data(group_id=message.text)
    try:
        # заодно проверит, есть ли введенный id в подгруппе:
        subgroups_list = list(input_data['subgroups_dict'][message.text])
    except:
        groups_list = list(input_data['subgroups_dict'])
        await message.answer(text='Ошибка ввода, повторите, пожалуйста, еще раз:')
        await message.answer(text='<b>Выберите группу приборов</b> Group ID:', parse_mode='html',
                             reply_markup=kb.groups_kb(groups_list))
        await WorkStates.group_id.set()
        return
    # продолжаем:
    await message.answer(text='<b>Выберите подгруппу приборов</b> (SubGroup):', parse_mode='html',
                         reply_markup=kb.subgroups_kb(subgroups_list))
    await WorkStates.subgroup.set()


@dp.message_handler(state=WorkStates.subgroup)
async def set_subgroup(message: Message, state) -> None:
    global input_data
    await state.update_data(subgroup=message.text)
    statedata = await state.get_data()
    try:
        complects_list = input_data['subgroups_dict'][statedata['group_id']][message.text]
    except:
        # еще раз на шаг назад:
        subgroups_list = list(input_data['subgroups_dict'][statedata['group_id']])
        await message.answer(text='Ошибка ввода, пожалуйста, повторите попытку:')
        await message.answer(text='<b>Выберите подгруппу приборов</b> (SubGroup):', parse_mode='html',
                             reply_markup=kb.subgroups_kb(subgroups_list))
        await WorkStates.subgroup.set()
        return
    # продолжаем, если погруппа нашлась в словаре подгрупп
    await message.answer(text='<b>Выберите устанавливаемый комплект</b> Complect ID:', parse_mode='html',
                         reply_markup=kb.complects_kb(complects_list))
    await WorkStates.complect.set()


@dp.message_handler(state=WorkStates.complect)
async def set_complect(message: Message, state) -> None:
    global input_data
    await state.update_data(complect_id=message.text)
    sd = await state.get_data()  # sd -- state data
    # выполняем проверки:
    step_back: bool = False
    # проверяем, является ли введенный текст номером комплекта:
    complects_list = input_data['subgroups_dict'][sd['group_id']][sd['subgroup']]
    if not message.text in complects_list:
        await message.answer(text='Ошибка ввода, пожалуйста, повторите попытку.')
        step_back = True
    else:
        # проверяем, не занят ли этот прибор кем-то другим на другой точке:
        ds = list(db.get_complect(message.text))  # ds -- device status
        if ds[1] != 'свободен':
            await message.answer(text=f'Внимание: прибор {ds[0]} уже зарегистрирован '
                                      f'на точке {ds[2]} пользователем с ID {ds[3]} в {ds[4]}!')
            await message.answer(text=f'Уточните, пожалуйста, данные у специалиста с ID {ds[3]} и повторите попытку.')
            step_back = True
    if step_back:
        # просим ввести еще раз, и машина состояний на шаг назад:
        await message.answer(text='<b>Выберите устанавливаемый комплект</b> Complect ID:', parse_mode='html',
                             reply_markup=kb.complects_kb(complects_list))
        await WorkStates.complect.set()
        return
    # проверяем
    # если все прошло успешно продолжаем заполнять:
    datetime_start = message.date
    lat = input_data[f'{message.from_user.id}'][0]
    lon = input_data[f'{message.from_user.id}'][1]
    db.set_point_start(sd['point_id'], lat, lon, sd['complect_id'], int(message.from_user.id), str(datetime_start))
    logger.info(f'{datetime_start} начало регистрации прибора {sd["complect_id"]} на точке {sd["point_id"]} '
                f'специалистом {message.from_user.id} @{message.from_user.username}')
    await message.answer(text=f'Отправлено <b>{sd["point_id"]}</b> {sd["complect_id"]} {datetime_start} {lat} {lon}',
                         parse_mode='html', reply_markup=kb.work_menu_kb)
    await state.finish()


@dp.message_handler(text='Снять прибор')
async def pick_device_up(message: Message) -> None:
    if db.user_started_work(message.from_id) == 0:
        await message.answer(text='Ваш пользователь не отмечен в поле.\nПожалуйста, нажмите "Начать работу".')
        return
    await message.answer(text='<b>Выберите имя точки, на которой завершаете рагистрацию:</b>', parse_mode='html',
                         reply_markup=kb.points_kb(input_data['Point_ID']))
    await EndStates.pickup_point_id.set()


@dp.message_handler(state=EndStates.pickup_point_id)
async def pick_device_up_from_point(message: Message, state) -> None:
    await state.update_data(pickup_point_id=message.text)
    sd = await state.get_data()  # sd -- state data
    datetime_end = str(message.date)
    # записываем отметку об окончании регистрации в db:
    answer = db.set_point_end(point_id=sd['pickup_point_id'], datetime_end=datetime_end)
    await message.answer(text=answer)

    # и отмечаем, что прибор свободен:
    pickup_point = db.get_point(sd['pickup_point_id'])
    complect_id = pickup_point[1]
    answer = db.set_complect_free(complect_id=complect_id)
    await message.answer(text=answer)
    await state.finish()


@dp.callback_query_handler(lambda callback_query: json.loads(callback_query.data)['#'] == 'Groups')
async def device_description(call: CallbackQuery):
    callback_data = call.data
    callback_data = json.loads(callback_data)
    GroupID = str(callback_data['GroupID'])
    device_model, description, url = utils.get_devices_description(GroupID=GroupID)
    caption = f'<b>{device_model}</b>\n\n{description}'
    with open(settings.device_image(device_group=GroupID), 'rb') as photo:
        await call.message.answer_photo(photo=photo, caption=caption,
                                        parse_mode='html', reply_markup=kb.url_kb(url))
    await call.answer()


@dp.message_handler()
async def all_messages(message: Message) -> None:
    await message.answer('Команда не распознана, для начала, пожалуйста, нажмите на /start или /menu')


def main(skip_updates: bool = True, echo: bool = False) -> None:
    global input_data
    # Расположение задания и других json-данных от приложения (app)
    # передается вторым (т.е. [1]) аргументом в команде запуска бота:
    if echo:
        for j, param in enumerate(sys.argv):
            print(f'аргументы: sys.argv[j] = {param}')
        print('Количество аргументов:', len(sys.argv))

    # читаем и декодируем из json, если файл передан:
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            input_data = json.load(file)
        if echo:
            print('Распаковка json:\n', input_data)
        print(f'bot-main: параметры входного задания получены в {sys.argv[1]}')

    # Запуск основного цикла telegram-бота:
    executor.start_polling(dp, skip_updates=skip_updates, on_startup=on_startup)

if __name__ == '__main__':
    main()