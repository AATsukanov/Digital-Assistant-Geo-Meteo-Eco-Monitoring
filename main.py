# ставим python 3.9
# ставим aiogram 2.25.1

# импорт сторонних библиотек
import tkinter as tk
import asyncio
import threading
import logging
import time

# для телеги:
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
#from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
#from aiogram.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# импорт своих модулей
import config
import keyboards as kb
#import admin
import database as db
#import texts

