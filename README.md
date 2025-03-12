# ЦИФРОВОЙ АССИСТЕНТ СИСТЕМЫ ГЕОМОНИТОРИНГА Lite

#### Алексей Алексеевич ЦУКАНОВ (c) 2024
#### alexey@tsukanoff.ru

## Цель:
Разработать и реализовать программный комплекс 
«Цифровой ассистент системы геомониторинга» для использования в центрах геомониторинга
(метеорологических, экологических, геофизических и пр.), упрощающий работу 
с регистрирующими приборами и обмен данными при проведении полевого этапа 
работ, а также взаимодействие специалистов полевого отряда между собой и с 
координационным центром. Здесь представлена версия ***Lite*** ограниченной функциональности, 
версия Pro недоступна в виде *open source*. 

## Использованные библиотеки, *фреймворки* и технологии

    Tkinter, Telegram, SQLite, Pandas, Threading, API статических карт Яндекса 

Разработанный программный комплекс состоит из двух связанных между собой программ: основное
*desktop*-приложение с графическим интерфейсом, 
реализованное с помощью библиотеки **tkinter** и telegram-бот, реализованный
с использованием библиотеки **aiogram** версии 2.25.2. 
Основной язык программирования **Python 3** (использовалась версия 3.9), 
базы данных реализованы с использованием **SQLite 3**.
В работе с исходными данными в формате xlsx-файлов применялась библиотека **pandas** 
в связке с **openpyxl**. 

Для обмена основными данными между *desktop*-приложением и
telegram-ботом использовались базы данных, вспомогательные параметры передавались при
запуске telegram-бота с использованием возможностей *упаковки-распаковки* библиотеки **json**. 
После загрузки необходимых данных и формирования *проекта-задания* из основного приложения
выполняется запуск telegram-бота в параллельном потоке с передачей необходимых параметров.


## ОПИСАНИЕ

## Краткое описание баз данных

В проекте создаются и используются 2 базы данных, которые располагаются в папке **databases/**:

    - users.db содержит 2 таблицы: Users, Admins
    - project.db содержит 2 таблицы: Points, Devices

Таблица Users содержит данные о полевых специалистах, который выполняют расстановку приборов 
согласно проектному заданию. 
В таблице Admins содержаться необходимые данные о координаторах проекта.

База данных **project.db** обновляется при формировании задания полевых работ на день,
в таблицу **Points** заносится список уникальных названий точек (и их координаты), рядом с которыми
необходимо установить прибор. В таблицу **Devices** записывается список ID приборов, эта
таблица служит вспомогательной, позволяя во время установки приборов вести учет комплектов.

Работа с ними осуществляется через библиотеку sqlite3, crud-функции прописаны в 
python-модуле проекта **database.py**.

Формально к базам данных можно отнести также и статическую таблицу с описанием 
***приборной базы***, которая используется только для чтения и располагается в проекте
в директории **tables/** в формате xlsx-файла (сейчас это файл: DevicesInfo.xlsx).

## Описание хода работ при использовании программы

Cпециалисты из группы Admins с использованием основной *desktop*-программы создают *Задание* 
на день, которое включает в себя таблицу точек, содержащую плановые (не фактические) 
координаты точек (в системе WGS84), список названий точек и рекомендуемую для 
использования группу приборов (выбираются по названию группы GroupID из таблицы Devices). 

Кроме того, формируется описание проекта / задания, и с помощью ***API статических карт 
Яндекса*** (https://yandex.ru/maps-api/products/static-api) генерируется карта территории с расположениями этих точек.

*Задание* при запуске telegram-бота из основного *desktop*-приложения становится доступно
полевым специалистам со смартфона или планшета (необходим аккаунт в Telegram, наличие в устройстве
модуля GPS | ГЛОНАСС, доступ в интернет).

Функционал telegram-бота позволяет выйти со смартфоном на точку, выбрать ее имя из меню, 
просмотреть и выбрать тип прибора, установить его и затем, нажав на кнопку, 
зарегистрировать на сервере данные об установке прибора, включая название точки, 
уникальное ID прибора, время установки, фактические координаты в WGS84 и уникальное 
ID специалиста, выполнившего постановку измерительной аппаратуры.

В процессе работы функционал telegram-бота позволяет просмотреть актуальную информацию
об установленных приборах, оставшихся точках, участниках полевого отряда и много другое.
Имеется возможность посмотреть информацию о приборной базе, включая изображение приборов,
описание и ссылки на сайт производителя. Также есть возможность просмотреть краткую
инструкцию о работе telegram-бота, связаться с разработчиком и координационным центром.
Функционал telegram-бота дает возможность вывести свои координаты на экран и 
открыть свою геопозицию на web-картах, сейчас (в версии 0.0.1) реализована поддержка 4 сервисов через 
формирование URL-запросов в **Яндекс**-карты, **OpenStreetMap** (**OSM**), **Google maps** и 
сайт **nakarte.me**.

В конце полевого дня, специалисты снова возвращаются на точки и, отключая/собирая аппаратуру, 
также через функционал telegram-бота отправляют данные об окончании регистрации
-- сервер пишет отправляемые ему данные, как об установке так и снятии приборов, 
включая данные о времени, фактических координатах и о том, кто именно произвел 
работы на каждой конкретной точке. 
Формируются данные для полевого журнала и блока в отчет.


## Структура проекта

Файловая структура проекта представлена на ***Рис.0.:*** основное приложение (входная точка) 
пакета программ находится в модуле **app.py**, в нем прописана вся логика tkinter-приложения.
Основной модуль telegram-бота находится в файле **main.py**, клавиатуры и функции, создающие
клавиатуры, вынесены в отдельный python-файл **keyboards.py**. Основные настройки пакета
содержатся в python-файле **config.py**, общие настройки, которые в будущем рекомендую перенести
в интерфейс содержатся в **settings.py**.

![структура папок проекта](https://github.com/user-attachments/assets/2946d074-9c95-4a94-a0d8-4d296b4730b0)
***Рис.0.*** *Структура каталогов проекта.*

Модуль с CRUD-функциями находится в **database.py** файле. Вспомогательные *классы* и 
*датаклассы* прописаны в **datatypes.py**. 

В модуле **logger.py** определяется *"логгер"* на базе библиотеки **logging**, 
способный одновременно направлять *лог*-информацию в файл (лог-файлы сохраняются в каталоге 
**logs/**) и в терминал/консоль.

Модуль **earth.py** содержит методы формирования URL-запросов для построения растровых статических
карт и обращения к сервисам web-карт.

В корневом каталоге проекта находятся еще и вспомогательные **py**-файлы **utils.py** и **docs.py**,
названия которых говорят сами за себя, а также оригинальная иконка **icon.ico**, созданная для приложения,
файл необходимых сторонних модулей виртуального окружения **requirements.txt** и в формате
*markdown* инструкция **README.md** разработанного пакета, включающая техническую информацию и 
описание примера работы с ним. Отдельно стоит отметить, что в корневой папке
исходного проекта имеется **py**-файл **tsukanoff.py**, который добавлен в *.gitignore*, поскольку
в нем содержится непубличная информация, например token от Telegram Bot Father, который в случае
использования настоящего пакета программ, необходимо получить самостоятельно (https://core.telegram.org/bots). 
Данные из **tsukanoff.py** импортируются только в модуле **config.py**, где в комментариях даны
необходимые пояснения относительно назначения каждой переменной.

### Каталоги:

    databases/ - каталог размещения баз данных *.db
    img/ - каталог изображений: фото приборов, стартовый рисунок telegram-бота, фоновый рисунок окна tkinter
    logs/ - каталог сохранения log-файлов
    params/ - каталог для файлов обмена (*.json) между основным приложением и telegram-ботом
    tables/ - каталог размещения вспомогательных xlsx-файлов
    temp_maps/ - каталог сохранения временных файлов с растровыми картами


## Работа с tkinter-модулем приложения "Цифровой ассистент системы геомониторнга"

### Работа с основным функционалом на примере проекта "10 вершин Кавказских гор"

![01](https://github.com/user-attachments/assets/0d69b340-7787-408a-a643-389338727f15)

***Рис.1.***

Начальное (основное) окно *desktop*-модуля программы "Цифровой ассистент системы геомониторнга" версии 0.0.1 показано на ***Рис.1***. 
Для демонстрации работы с программой был сделан тестовый проект с названием *"10 вершин Кавказа"*. 
Исходные данные представляют собой таблицу, содержащую 10 точек в координатной системе WGS84 с формальными именами точек P01, ..., P10 
(каждая точка соответствует положению одного из пиков Кавказских гор из списка топ-10 по высоте).
Далее будем назвать эту таблицу *таблицей точек*.

![02](https://github.com/user-attachments/assets/44c86136-4f68-407c-bbc4-2880cf4e5d3d)

***Рис.2.***

Для загрузки таблицы точек из xlsx-файла нужно воспользоваться основным Меню -> Файл -> "Открыть задание из *.xlsx"
и выбрать нужный файл (в нашем примере это файл из папки **tables/** *...Ten peaks...*, ***Рис.2***).

![03](https://github.com/user-attachments/assets/3d3a5715-6406-4f23-85e0-0600219d5d37)

***Рис.3.***

После загрузки файла с проектными точками, программа сформирует запрос и получит сгенерированную
растровую карту Яндекс с отмеченными на ней точками из загруженной таблицы. Пример для нашего
тестового проекта представлен на *скриншоте* ***Рис.3***.

![04](https://github.com/user-attachments/assets/f3adaf88-544f-4dcf-83ba-4667c7879b55)

***Рис.4.***

Некоторую статистическую информацию по проекту можно посмотреть в Меню -> Проект -> "Статистика проекта",
как показано на ***Рис.4***. 

![05](https://github.com/user-attachments/assets/bbf5cbcb-cde4-47ad-84f8-afd1266486c8)

***Рис.5.***

В результате откроется *MessageBox* с параметрами проекта, как количество точек, исходный файл,
из которого были загружены точки, диапазоны min-max значений долготы и широты в проекте и
*"правило"* формирования названий точек на примере первой и последней точки из списка 
(*см.* ***Рис.5***).

![06](https://github.com/user-attachments/assets/e65e06d6-0e4e-4197-98c3-b6e032078292)

***Рис.6.***

Для дальнейшей работы необходимо сначала сформировать *Задание*, для чего нужно пройти в основном меню
на вкладку Проект -> "Создать проектное задание", как показано на ***Рис.6***.

![07](https://github.com/user-attachments/assets/5a7788f3-cc6c-4512-afe9-6c182f4a568e)

***Рис.7.***

Далее будет предложено заполнить такие поля как:

* Название проекта или задания (***Рис.7.***)
* Список групп рекомендованных приборов (***Рис.8.***)
* Выбрать файл с таблицей комплектов приборов (***Рис.9***) и загрузить его (***Рис.10.***), для нашего проекта он лежит в *tables/TableOfComplects.xlsx*.
* Заполнить описание к заданию, важные замечания, детали проекта, особенности проведения полевых работ для конкретных условий и т.д. (***Рис.11.***) 
Это описание будет доступно группе полевых специалистов через функционал telegram-бота.


![08](https://github.com/user-attachments/assets/eba70359-6113-47c6-b1a5-770a4c49e960)

***Рис.8.***


![09](https://github.com/user-attachments/assets/bd7c64f3-3bb3-4071-b249-6d097e31934e)

***Рис.9.***


![10](https://github.com/user-attachments/assets/85aa92f5-3021-4ef9-b6e2-e48f257dee03)

***Рис.10.***



![11](https://github.com/user-attachments/assets/8b4361e8-d51c-4bf8-9ff0-c79d86017e87)

***Рис.11.***



![12](https://github.com/user-attachments/assets/a60bfb00-8aef-4bfe-a586-9c718c0394c6)

***Рис.12.***

После этого все необходимые параметры и базы данных будут сформированы и готовы для их 
использования в telegram-боте (***Рис.12***).

![13](https://github.com/user-attachments/assets/beac653e-a00b-499e-bfb7-6deea9bf2a3f)

***Рис.13.***

Запуск Telegram-бота осуществляется через пункт основного меню *desktop*-приложения:
"Меню" -> "Telegram-бот" -> "Запустить Telegram-бота",
как это продемонстрировано на *скриншоте* ***Рис.13.***

### Второстепенные пункты меню программы
![A1](https://github.com/user-attachments/assets/5440f0dc-9cae-4152-bc6e-36ae6c97f310)

***Рис.П1.*** Вкладка меню "Управление БД".


![A2](https://github.com/user-attachments/assets/9006d253-124d-4aea-8a02-271bc8a8e6d5)

***Рис.П2.*** Вкладка меню "О программе"...


![A3](https://github.com/user-attachments/assets/ebaf3075-944d-43da-ab06-1fd17943e679)

***Рис.П3.*** Сообщение с контактами разработчика.


![A4](https://github.com/user-attachments/assets/84e06f85-240f-4fd4-9619-a7efcb3c800a)

***Рис.П4.*** Сообщение со сведениями о программе, её версии и текущей конфигурации ПК и ОС.



## Пример работы с telegram-ботом пакета "Цифровой ассистент системы геомониторнга"



![01](https://github.com/user-attachments/assets/ca649a0f-289c-45e3-8816-c5123a21e43f)
### СКРИНШОТ 1 - Приветственное сообщение и главное меню (клавиатура) бота.

![02](https://github.com/user-attachments/assets/ba351083-ea1c-470d-8be2-6f6e9307bf55)
### СКРИНШОТ 2 - Клавиша "Открыть задание" демонстрирует растровую карту с плановыми точками, которую мы видели в основном приложении (***Рис.3***), описание задания и название проекта.

![03](https://github.com/user-attachments/assets/c37e2c43-e95b-4032-87a3-fe3ec2c79fb0)
### СКРИНШОТ 3 - Кнопка "Свой профиль" открывает данные пользователя (не admin-пользователя), есть возможность *подгрузки* и редактирования.

![04](https://github.com/user-attachments/assets/881e0871-1e48-4131-8387-4d7f5b29652f)
### СКРИНШОТ 4 - Кнопка "Проверить свою геолокацию". Запрос подтверждения отправки координат своего местоположения боту. 

![05](https://github.com/user-attachments/assets/02f04d73-b1a0-4096-9823-953d85e88534)
### СКРИНШОТ 5 - Получение своих координат и *инлайн-клавиатура* с выбором из четырех web-карт.

![06](https://github.com/user-attachments/assets/1915f614-520e-4768-a0b7-ef40ad8984e4)
### СКРИНШОТ 6 - Пример результата перехода на *OpenStreetMap* сервис.

![07](https://github.com/user-attachments/assets/772df49b-4014-4a8f-9b3f-5669795a5dad)
### СКРИНШОТ 7 - Клавиша "Приборная база" выдает клавиатуру с обозначениями групп имеющихся приборов.

![08](https://github.com/user-attachments/assets/ef780607-6f75-46c3-81bc-268af376e854)
### СКРИНШОТ 8 - Пример для группы приборов "A" (Acoustic...).

![09](https://github.com/user-attachments/assets/0e6f307b-2550-4065-9b0d-27b35cd20e64)
### СКРИНШОТ 9 - Пример для группы приборов "B" (Bots...).

![10](https://github.com/user-attachments/assets/032c2182-a823-4a8d-bea6-da3e90816ddf)
### СКРИНШОТ 10 - Пример для группы приборов "R" (Rain, snow...).

![11](https://github.com/user-attachments/assets/525ea1d6-8960-4689-9fbf-a2715e75823b)
### СКРИНШОТ 11 - Пример для группы приборов "W" (Wind...).

![12](https://github.com/user-attachments/assets/01d0c716-157d-42df-a778-441c5cd98652)
### СКРИНШОТ 12 - Возвращение на главное меню и последующий выбор "Начать работу".

![13](https://github.com/user-attachments/assets/5cb06235-7e57-49bd-b772-eaf67f313394)
### СКРИНШОТ 13 - Пример выполнения "Текущий прогресс" -> "Проектные точки (оставшиеся)".

![14](https://github.com/user-attachments/assets/0e79ea83-d44f-417d-a609-0e2cf5532c47)
### СКРИНШОТ 14 - Пример выполнения "Текущий прогресс" -> "Список свободных приборов".

![15](https://github.com/user-attachments/assets/998901ac-e1d9-4887-aff4-c4a2709d6866)
### СКРИНШОТ 15 - Кнопка "Установить прибор (запрос геолокации)" и ответ с *инлайн-клавиатурой*.

![16](https://github.com/user-attachments/assets/1edaf108-9623-4230-9565-819281e03487)
### СКРИНШОТ 16 - Кнопка "Зарегистрировать точку" и запрос на имя точки из списка точек *Задания*.

![18](https://github.com/user-attachments/assets/3845eff8-b748-497c-9af8-52027bed06ba)
### СКРИНШОТ 17 - Последовательный ввод (через ***машину состояний***) ID группы (типа) прибора, подгруппы и номера (ID) устанавливаемого комплекта.

![19](https://github.com/user-attachments/assets/b5ae9de8-f518-42a3-bce9-e57bd691e744)
### СКРИНШОТ 18 - Успешная регистрация установки прибора W01 в точке P01 с фактическими координатами и отметкой времени.

![20](https://github.com/user-attachments/assets/e9c4fa85-09d7-47c3-a918-b2f2b38089bf)
### СКРИНШОТ 19 - Проверка обновленного состояния БД: "Текущий прогресс"->"Проектные точки (с приборами)".

![21](https://github.com/user-attachments/assets/55c9d47c-fb10-4838-889a-91ad3c931258)
### СКРИНШОТ 20 - Проверка обновленного состояния БД: "Текущий прогресс"->"Комплекты приборов (на точках)".

![22](https://github.com/user-attachments/assets/1c344276-9e41-4128-b17d-77ea91754403)
### СКРИНШОТ 21 - Кнопка "Снять прибор" с последующим выбором имени точки и отметкой о том, что изменения записаны в БД.

## Админ-панель

**Также в telegram-боте реализована ***admin-панель***, в ее функционал входит просмотр сведений о пользователях и возможность активации и деактивации аккаунтов.
Скриншоты ее работы здесь не представлены. Функции управления прописаны в main.py, клавиатуры в keyboards.py**.

## Список необходимых сторонних библиотек

    aiogram==2.25.2
    aiohttp==3.8.6
    aiosignal==1.3.1
    async-timeout==4.0.3
    attrs==24.2.0
    Babel==2.9.1
    certifi==2024.8.30
    charset-normalizer==3.4.0
    et_xmlfile==2.0.0
    flake8==7.1.1
    frozenlist==1.5.0
    idna==3.10
    magic-filter==1.0.12
    mccabe==0.7.0
    multidict==6.1.0
    numpy==2.0.2
    openpyxl==3.1.5
    pandas==2.2.3
    propcache==0.2.0
    pycodestyle==2.12.1
    pyflakes==3.2.0
    python-dateutil==2.9.0.post0
    pytz==2024.2
    six==1.16.0
    typing_extensions==4.12.2
    tzdata==2024.2
    yarl==1.18.0

## ЗАКЛЮЧЕНИЕ

Разработан и реализован функциональный программный комплекс "Цифровой ассистент системы геомониторинга",
состоящий из *desktop*-приложения и Telegram-бота, позволяющий формировать и сопровождать в реальном
времени и в реальных полевых условиях работы по установке аппаратуры геомониторинга для задач
метеорологии, экологии, геофизики и других направлений, базирующихся на наблюдениях за окружающей средой.

Программный комплекс поддерживает базовый функционал, который может быть в дальнейшем развит и
дополнен.

***Алексей Цуканов, 02.12.2024.***

https://scholar.google.ru/citations?user=4LlptA8AAAAJ&hl=ru&oi=ao

https://tsukanov-lab.moy.su/index/tsukanov_lab/0-2

https://orcid.org/0000-0003-2706-2247

https://github.com/AATsukanov






