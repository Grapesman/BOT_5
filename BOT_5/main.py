import os
from dotenv import load_dotenv
load_dotenv()
import Yandex_disk, Functions, Graph, Telegram
#Вызываем файл с функцией загрузки Excel файла с Яндекс-диска
Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------ВЫПОЛНЕНИЕ ФУНКЦИЙ ДЛЯ 1 КОМАНДЫ--------------------------------------------
# Считаем количество строк в файле по листу "Каталог статей"
stroki = Functions.how_much_string(os.getenv('SAVE_PATH'))
# Считаем количество строк в файле по листу "Community"
stroki_community = Functions.how_much_string_community(os.getenv('SAVE_PATH'))
# Формируем словарь с фамилиями и тегами с листа "Community"
data_dict = Functions.make_dict(os.getenv('SAVE_PATH'))

# Проверяем поочередно условия для листа "Каталог статей"
# Проверка первого условия
FIOs_without_name = Functions.f_FIOs_without_name(os.getenv('SAVE_PATH'))
Fs_without_name = Functions.f_Fs_without_name(FIOs_without_name)
Familys_without_name = Functions.f_Familys_without_name(Fs_without_name)

# Проверка второго условия
FIOs_without_date = Functions.f_FIOs_without_date(os.getenv('SAVE_PATH'))
Fs_without_date = Functions.f_Fs_without_date(FIOs_without_date)
Familys_without_date = Functions.f_Familys_without_date(Fs_without_date)

# Проверка третьего условия
FIOs_without_thesis = Functions.f_FIOs_without_thesis(os.getenv('SAVE_PATH'))
Fs_without_thesis = Functions.f_Fs_without_thesis(FIOs_without_thesis)
Familys_without_thesis = Functions.f_Familys_without_thesis(Fs_without_thesis)

# Проверка четвертого условия
FIOs_without_key = Functions.f_FIOs_without_key(os.getenv('SAVE_PATH'))
Fs_without_key = Functions.f_Fs_without_key(FIOs_without_key)
Familys_without_key = Functions.f_Familys_without_key(Fs_without_key)

# Проверка пятого условия
# Находим статьи, с заполненным названием, но без автора
names_state = Functions.f_state_name(os.getenv('SAVE_PATH')) #<--------- это выводим в бот в команде ["status"]
# Объединяем все полученные списки (1-4 условий) с фамилиями в один список
result = Functions.f_result_Familys (Familys_without_name, Familys_without_date, Familys_without_thesis, Familys_without_key)
# Исключаем повторы фамилий в списке
without_duplication = Functions.remove_duplicates(result)
# По получившимся фамилиям находим теги из словаря
all_teg = Functions.teg_function(without_duplication) #<--------- это выводим в бот в команде ["status"]
# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------ВЫПОЛНЕНИЕ ФУНКЦИЙ ДЛЯ 2 КОМАНДЫ--------------------------------------------
# Сохраняем список дат публикации статей
DATA = Functions.date_check(os.getenv('SAVE_PATH'))
# Сохраняем названия статей
STATE = Functions.name_check(os.getenv('SAVE_PATH'))
# Сохраняем список дат создания статей
MAKE = Functions.make_check(os.getenv('SAVE_PATH'))

# Создаем словарь DATA & STATE
DICT_DATA_STATE = Functions.function_DICT_DATA_STATE(DATA, STATE)
# Создаем словарь STATE & MAKE
DICT_STATE_MAKE = Functions.function_DICT_STATE_MAKE(STATE, MAKE)

# Определяем даты публикации, относительно текущей, в диапазоне до 180 дней и сохраняем в виде списка
checking = Functions.compare_dates()

# Убираем повторяющиеся даты из списка
state_3m = Functions.remove_duplicates_3m(checking)

# Сохраняем список статей по данным датам
check_state_in_dict = Functions.state_function(state_3m, DICT_DATA_STATE)

# Находим даты создания статьи по её названию
check_make_in_dict = Functions.make_function(check_state_in_dict, DICT_STATE_MAKE)

# Переводим списки дат создания и публикации из формата date в формат datetime
date_check_make_in_dict = [dt.date() for dt in check_make_in_dict]
date_state_3m = [dt.date() for dt in state_3m]

# Вызываем файл Graph и создаем график
Graph.make_graph(check_state_in_dict, date_check_make_in_dict, date_state_3m)
# Вызываем файл Telegram и запускаем бота
Telegram.bot(os.getenv('TOKEN_bot'), all_teg, names_state)
# ----------------------------------------------------------------------------------------------------------------------