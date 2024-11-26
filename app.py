import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.filedialog as tkfd
import tkinter.simpledialog as tksd
import os

import config
import settings

class App(tk.Tk):

    def __init__(self):
        super().__init__()  # запуск инициализации родительского класса
        self.init_GUI()

    def init_GUI(self):
        self.title(f'{config.app_title} {config.version}')
        self.geometry(config.geometry)
        self.resizable(width=False, height=False)  # пока отключим возможность изменения размеров основного окна
        self.iconbitmap(config.iconbitmap)
        self.iconify = True

        # Перехват закрытия окна:
        self.protocol('WM_DELETE_WINDOW', self.on_quit)

        # Основное управление в виде menu bar:
        self.MenuBar = tk.Menu(self)
        # Menu->File:
        self.menu_file = tk.Menu(self.MenuBar, tearoff=0)
        self.menu_file.add_command(label=u'Открыть задание из *.xlsx', command=self.on_open_xlsx)
        self.menu_file.add_command(label=u'Загрузить проект из *.kml', command=self.on_open_kml)
        self.menu_file.add_separator()
        self.menu_file.add_command(label=u'Статистика проекта', command=self.on_project_stat)
        self.menu_file.add_command(label=u'Сведения', command=self.on_about)
        self.menu_file.add_separator()
        self.menu_file.add_command(label=u'Выход', command=self.on_quit)
        self.MenuBar.add_cascade(label=u'Файл', menu=self.menu_file)

        # Menu->Telegram Bot:
        self.menu_tg_bot = tk.Menu(self.MenuBar, tearoff=0)
        self.menu_tg_bot.add_command(label='Запустить Telegram-бота', command=self.on_run_telegram_bot)
        self.menu_tg_bot.add_command(label='Настройки бота', command=self.on_bot_settings)
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

    def on_open_xlsx(self):
        pass

    def on_open_kml(self):
        pass

    def on_project_stat(self):
        pass

    def on_run_telegram_bot(self):
        print('Запуск Telegram-бота...')
        os.system('python main.py')

    def on_app_settings(self):
        pass

    def on_bot_settings(self):
        pass

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
    print(f'{config.app_title}, версия = {config.version}')
    print(f'(by {config.AuthorInfo.author})')
    app = App()
    app.mainloop()

# MAIN:
if __name__ == '__main__':
    main()