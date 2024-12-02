
instruction_ru: str = """
<b>КРАТКОЕ РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ</b>\n
<b>Описание хода работ при использовании программы</b>\n

Cпециалисты из группы Admins (координаторы проекта) с использованием основного desktop-программы создают "Задание" 
на день, которое включает в себя таблицу точек, содержащую плановые (не фактические) 
координаты точек (в системе WGS84), список названий точек и рекомендуемую для 
использования группу приборов (выбираются по названию группы GroupID из таблицы Devices). 

Кроме того, формируется описание проекта / задания, и с помощью API статических карт 
Яндекса генерируется карта территории с расположениями этих точек.

"Задание" при запуске telegram-бота из основного desktop-приложения становиться доступно
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
открыть свою геопозицию на web-картах (сейчас реализована поддержка 4 сервисов через 
формирование URL-запросов в Яндекс-карты, OpenStreetMap (OSM), Google maps и 
сайт nakarte.me).

В конце полевого дня, специалисты снова возвращаются на точки и, отключая/собирая аппаратуру, 
также через функционал telegram-бота отправляют данные об окончании регистрации
-- сервер пишет отправляемые ему данные, как об установке так и снятии приборов, 
включая данные о времени, фактических координатах и о том, кто именно произвел 
работы на каждой конкретной точке. 
Формируются данные для полевого журнала и блока в отчет.
"""