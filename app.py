import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.filedialog as tkfd
import tkinter.simpledialog as tksd
import os
import threading
import datetime

import pandas as pd

# импортируем свои модули
import config
import settings
from datatypes import Task
from earth import StaticEarth

def onewtreadecorator(func):
    '''Декорируем функции, которые хотим запустить в параллельном потоке'''
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=lambda: func(*args, **kwargs))
        thread.start()
    return wrapper

class App(tk.Tk):

    def __init__(self):
        super().__init__()  # запуск инициализации родительского класса
        self.task = Task()  # объект задания
        self.fname_map_image: str = ''  # растровая карта
        self.init_GUI()

    def init_GUI(self):
        self.title(f'{config.app_title} {config.version}')
        self.geometry(settings.geometry)
        self.resizable(width=False, height=False)  # пока отключим возможность изменения размеров основного окна
        self.iconbitmap(config.iconbitmap)
        self.iconify = True

        # Перехват закрытия окна:
        self.protocol('WM_DELETE_WINDOW', self.on_quit)

        # "Холст" для вывода изображения карты:
        self.canvas = tk.Canvas(self, height=450, width=650)  # у статических Я.карт 650х450 максимальное разрешение
        self.photo_image = tk.PhotoImage(file=settings.canvas_bg_img)
        self.img_tag = self.canvas.create_image(0, 0, anchor='nw', image=self.photo_image)
        self.canvas.grid(row=0, column=0)

        # Основное управление в виде menu bar:
        self.MenuBar = tk.Menu(self)
        # Menu->File:
        self.menu_file = tk.Menu(self.MenuBar, tearoff=0)
        self.menu_file.add_command(label='Открыть задание из *.xlsx', command=self.on_open_xlsx)
        self.menu_file.add_command(label='Загрузить проект из *.kml', state=tk.DISABLED, command=self.on_open_kml)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Статистика проекта', command=self.on_project_stat)
        self.menu_file.add_command(label='Сведения', command=self.on_about)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Выход', command=self.on_quit)
        self.MenuBar.add_cascade(label='Файл', menu=self.menu_file)

        # Menu->Проект:
        self.menu_project = tk.Menu(self.MenuBar, tearoff=0)
        self.menu_project.add_command(label='Загрузить таблицу точек из *.xlsx', command=self.on_open_xlsx)
        self.menu_project.add_command(label='Статистика проекта', command=self.on_project_stat)
        self.menu_project.add_separator()
        self.menu_project.add_command(label='Создать проектное задание', command=self.on_create_task)
        self.menu_project.add_separator()
        self.menu_project.add_command(label='Запустить Telegram-бота', command=self.on_run_telegram_bot)
        self.MenuBar.add_cascade(label='Проект', menu=self.menu_project)

        # Menu->Telegram Bot:
        self.menu_tg_bot = tk.Menu(self.MenuBar, tearoff=0)
        self.menu_tg_bot.add_command(label='Настройки бота', command=self.on_bot_settings)
        self.menu_tg_bot.add_separator()
        self.menu_tg_bot.add_command(label='Запустить Telegram-бота', command=self.on_run_telegram_bot)
        self.MenuBar.add_cascade(label='Telegram-бот', menu=self.menu_tg_bot)

        # Menu->Настройки:
        self.menu_settings = tk.Menu(self.MenuBar, tearoff=0)
        self.menu_settings.add_command(label='Настройки приложения', command=self.on_app_settings)
        self.menu_settings.add_command(label='Настройки бота', command=self.on_bot_settings)
        self.MenuBar.add_cascade(label='Настройки', menu=self.menu_settings)

        # Menu->About:
        self.menu_about = tk.Menu(self.MenuBar, tearoff=0)
        self.menu_about.add_command(label='Контакты', command=self.on_contacts)
        self.menu_about.add_command(label='О версии...', command=self.on_about)
        self.MenuBar.add_cascade(label='О программе', menu=self.menu_about)

        # Menu->Язык
        self.menu_language = tk.Menu(self.MenuBar, tearoff=0)
        self.language = tk.StringVar()
        self.language.set(settings.default_language)
        self.language.trace('w', self.on_change_language)
        #language_img = tk.PhotoImage(file=config.language_icon)
        self.menu_language.add_radiobutton(label='Русский (Ru)', value='Ru', variable=self.language)
        self.menu_language.add_radiobutton(label='中文 (Cn)', value='Cn', variable=self.language)
        #self.MenuBar.add_cascade(image=language_img, compound="left", menu=self.menu_language)
        self.MenuBar.add_cascade(label='Ru/中文', menu=self.menu_language)

        # configure:
        self.config(menu=self.MenuBar)


    def on_open_xlsx(self) -> None:
        fname = tkfd.askopenfilename(filetypes=[('Таблица Excel', '*.xlsx'), ('Все файлы', '*.*')])
        self.task.load(fname)
        earth = StaticEarth()
        # все метки -- обычные точки: 'Т':
        points_status = ['Т' for _ in range(self.task.nPoints)]
        earth.copy_points(longitude=self.task.E_WGS84,
                          latitude=self.task.N_WGS84,
                          status=points_status)
        fname_map = earth.load_map()
        if not fname_map == '':
            self.show_image(fname_map)
            self.fname_map_image =fname_map

    def on_open_kml(self):
        pass


    def on_create_task(self, echo=True) -> bool:
        if self.task.nPoints < 1:
            msg = 'Похоже, проект не загружен, либо не содержит плановых точек.\n'\
                  'Пожалуйста, загрузите Таблицу точек проекта:\nМеню -> Файл -> Открыть задание из *.xlsx'
            tkmb.showinfo(parent=self, title='Создание задания', message=msg)
            return False
        today = datetime.date.today()
        # Если точки загружены, заполняем поля self.task:
        # Название проекта:
        self.task.ProjectName = tksd.askstring(parent=self, title='Создание полевого задания',
                                               prompt='Пожалуйста, заполните название проекта или задания:',
                                               initialvalue=f'Проект геомониторинга {today.month}/{today.year}')
        # Group ID приборов:
        ask_one_more = True
        while ask_one_more:
            recommended_group_of_devices = tksd.askstring(parent=self, title='Создание полевого задания',
                                                          prompt='Введите через пробел GroupID рекомендуемых приборов:',
                                                          initialvalue=' '.join(settings.devices_groups)).upper()
            self.task.recommended_group_of_devices = list(recommended_group_of_devices.split(' '))
            ask_one_more = not self.check_devices_groups(self.task.recommended_group_of_devices)
        if echo:
            print(f'recommended_group_of_devices = {self.task.recommended_group_of_devices}')

        # Растровая карта:
        self.task.map_image = self.fname_map_image

        # Complect ID комплекты приборов:
        #  - сначала загружаем таблицу со всеми комплектами приборов:
        tkmb.showinfo(parent=self, title='Создание задания',
                      message='Выберете файл с Таблицей комплектов приборов (ComplectID) и загрузите его.')
        fname = tkfd.askopenfilename(filetypes=[('Таблица комплектов приборов', '*.xlsx'), ('Все файлы', '*.*')])
        self.task.load_table_of_complects(fname)

        #  - сравниваем и оставляем только те, которые из списка рекомендованных recommended_group_of_devices:
        df = self.task.df_of_complects.copy()
        df['new_mark'] = ['нет' for _ in range(len(df['GroupID']))]
        for j, gid in enumerate(self.task.df_of_complects['GroupID']):
            if gid in self.task.recommended_group_of_devices:
                df.iloc[j, df.columns.get_loc('new_mark')] = 'да'

        self.task.df_of_complects = df[df['new_mark'] == 'да']
        # убираем временный столбец и создаем подгруппы:
        self.task.df_of_complects = self.task.df_of_complects[['ComplectID', 'GroupID']]
        self.task.df_of_complects['SubGroups'] = self.task.df_of_complects['GroupID']
        for j, cid in enumerate(self.task.df_of_complects['ComplectID']):
            if str(cid).isdigit():
                if len(cid) < 2:
                    sub = '1-9'
                elif len(cid) < 3:
                    sub = f'{cid[0]}0-{cid[0]}9'
                else:
                    sub = '100+'
            else:
                if len(cid) < 4:
                    # еще как вариант: sub = f'{cid[:2]}0-{cid[:2]}9'
                    sub = f'{cid[:2]}[0-9]'
                else:
                    sub = f'{cid[0]}100+'
            self.task.df_of_complects.iloc[j, self.task.df_of_complects.columns.get_loc('SubGroups')] = sub

        # сохраняем в excel:
        fname = f'subgroups-of-complects.{today}.xlsx'
        Writer = pd.ExcelWriter(os.path.join(settings.tables_dir, fname))
        self.task.df_of_complects.to_excel(Writer, sheet_name='SubGroups', index=True)
        Writer._save()

        # Описание, комментарии к проведению полевых работ в свободной форме:
        self.task.TaskDetails = tksd.askstring(parent=self, title='Создание полевого задания',
                                               prompt='Описание, важные замечания к заданию, детали проекта, '
                                                      'особенности проведения полевых работ можно указать здесь '
                                                      '(в свободной форме) для полевых специалистов:',
                                               initialvalue='')

        # Дата формирования задания:
        self.task.date = datetime.date.today()
        return True

    def check_devices_groups(self, recommended_group_of_devices: list[str]) -> bool:
        err_msg = ''
        for group_id in recommended_group_of_devices:
            if not group_id in settings.devices_groups:
                err_msg += f'Group ID = {group_id} не определено\n'

        if err_msg != '':
            err_msg = 'Внимание: для поддерживаемых групп приборов\n' + err_msg
            tkmb.showwarning(parent=self, title='Проверка поддерживаемых приборов Group ID', message=err_msg)
            return False
        return True

    def on_project_stat(self):
        stat = 'Статистика проекта\n\n\n'
        stat += f'Загружено {self.task.nPoints} запланированных\nточек наблюдения.\n\n'
        stat += f'Исходная таблица точек проекта:\n{self.task.fname_project_points}\n\n'
        if self.task.nPoints > 0:
            stat += f'Сегмент значений широт:\nот {min(self.task.N_WGS84)} до {max(self.task.N_WGS84)}\n\n'
            stat += f'Диапазон значений долготы:\nот {min(self.task.E_WGS84)} до {max(self.task.E_WGS84)}\n\n'
            stat += f'Наименование ID точек:\nпервая {self.task.Point_ID[0]}, последняя {self.task.Point_ID[-1]}'
        else:
            stat += 'Похоже, проект не загружен, либо не содержит плановых точек.\n'\
                    'Пожалуйста, загрузите Таблицу точек проекта: Меню -> Файл -> Открыть задание из *.xlsx'
        tkmb.showinfo(parent=self, title='Статистика проекта', message=stat)

    @onewtreadecorator
    def on_run_telegram_bot(self):
        print('Запуск Telegram-бота...')
        cmd_line = f'python main.py {settings.fparams_json}'
        print(f'командой: {os.getcwd()}> {cmd_line}')
        os.system(cmd_line)

    def on_app_settings(self):
        tkmb.showinfo(parent=self, title='Настройка основного приложения',
                      message='Здесь будут добавлены настройки приложения,\nпока они производятся в файле setting.py.')

    def on_bot_settings(self):
        tkmb.showinfo(parent=self, title='Настройка Telegram-бота',
                      message='Здесь будут добавлены настройки Telegram-бота,\nпока они производятся в файле setting.py.')

    def show_image(self, fname: str):
        # Выводит изображение из файла на "холст":
        self.photo_image = tk.PhotoImage(file=fname)
        self.canvas.itemconfigure(self.img_tag, image=self.photo_image)

    def on_contacts(self):
        tkmb.showinfo(title='Контакты разработчика...',
                      message=f'"{config.app_title}"\n\n'
                              f'Идея и разработка:\n{config.AuthorInfo.author}\n\n'
                              f'e-mail:\n{config.AuthorInfo.author_email}\n\n'
                              f'страница автора:\n{config.AuthorInfo.author_page}\n\n'
                              f'сайт автора:\n{config.AuthorInfo.author_site}')

    def on_about(self):
        tkmb.showinfo(title='О программе / о версии...',
                      message=f'"{config.app_title}"\n\n'
                              f'Запущен из папки:\n{os.getcwd()}\n\n'
                              f'Версия ОС:\nos.name = {os.name}\n\n'
                              f'Количество CPU:\nos.cpu_count() = {os.cpu_count()}\n\n'
                              f'Версия пакета = {config.version}\n\n'
                              'Alexey A.Tsukanov (c) 2024.')

    def on_change_language(self, *args):
        tkmb.showinfo('Ru <-> Cn', '您好，抱歉，中文支援正在開發中。\n聯絡阿列克謝祖卡諾夫。')
        self.language.set(settings.default_language)

    def on_quit(self):
        if not tkmb.askyesno(title=u'Подтверждение выхода', message=u'Вы уверены, что хотите выйти?'):
            return
        self.destroy()

def main():
    print(f'"{config.app_title}", версия = {config.version}')
    print(f'(by {config.AuthorInfo.author})')
    app = App()
    app.mainloop()

# MAIN:
if __name__ == '__main__':
    main()