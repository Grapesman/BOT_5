import datetime
import warnings
import pandas as pd
from datetime import datetime
import logging
import re
from dateutil.parser import parse
from data_manager import DataManager


global check_state_in_dict
global date_check_make_in_dict
global date_state_3m
async def function2():
    # # СПИСОК ДЛЯ РЕАЛИЗАЦИИ 2 КОМАНДЫ
    a = []
    list_date_states = []  # Список для парсинга дат публикации статей с листа "Каталог статей"
    list_name_states = []  # Список для парсинга названий статей с листа "Каталог статей"
    list_make_states = []  # Список для парсинга дат создания статей с листа "Каталог статей"
    dict_date_name_state = {}  # словарь для объединения дат публикации и названий статей с листа "Каталог статей"
    dict_make_name_state = {}  # словарь для объединения дат создания и названий статей с листа "Каталог статей"
    date_2_list = []  # Список для сохранения дат статей, 6 и менее месяца от текущий с листа "Каталог статей"
    search_state = []  # Список статей для вывода в бот
    make_state = []  # Список дат создания по названию статей для вывода в бот
    global check_state_in_dict
    global date_check_make_in_dict
    global date_state_3m
    # Столбцы с названиями
    # B - "Название"
    # D - "Даты публикации"
    # F - "Тезиса"
    # H - "Авторы"
    # J - "Ключевые слова"

    # ----------------------------------------------------------------------------------------------------------------------
    # --------------------------------------------------ФУНКЦИИ 2 КОМАНДЫ---------------------------------------------------

    # РАЗДЕЛ ДЛЯ 2 КОМАНДЫ: ВЫВОД СТАТЕЙ НА БЛИЖАЙШИЕ 3 МЕСЯЦА

    # Функция определения количества заполненных строк. Определяем по столбцу "A" с нумерацией для листа "Каталог статей"
    def how_much_string(book):
        i = 1
        sheet = book['Каталог статей']
        while sheet['A' + str(i)].value is not None:
            a.append(i)
            i+=1
        return

    """-------------------------------------------------------------------------------------"""

    def date_check(book):
        sheet = book['Каталог статей']
        list_date_states = []

        for i in range(2, sheet.max_row + 1):
            try:
                cell_value = sheet[f'D{i}'].value

                if cell_value is None:
                    continue

                # Преобразуем значение в дату
                date_obj = smart_date_converter(cell_value)
                if date_obj:
                    list_date_states.append(date_obj)
                else:
                    logging.warning(f"Не удалось преобразовать в дату в строке {i}: {cell_value}")

            except Exception as e:
                logging.error(f"Ошибка в строке {i}: {e}")
                continue

        return list_date_states

    def smart_date_converter(value):
        """
        Умное преобразование различных форматов в datetime
        """
        if value is None:
            return None

        # Если уже datetime
        if isinstance(value, datetime):
            return value

        # Если pandas Timestamp
        if hasattr(value, 'to_pydatetime'):
            return value.to_pydatetime()

        # Преобразуем в строку для обработки
        str_value = str(value).strip()

        # Пробуем стандартные парсеры
        try:
            # 1. Пробуем pandas to_datetime (самый надежный)
            date_obj = pd.to_datetime(str_value, errors='coerce', dayfirst=True)
            if not pd.isna(date_obj):
                return date_obj.to_pydatetime()
        except:
            pass

        try:
            # 2. Пробуем dateutil.parser (понимает естественный язык)
            date_obj = parse(str_value, dayfirst=True, fuzzy=True)
            return date_obj
        except:
            pass

        # 3. Обработка числовых форматов
        if isinstance(value, (int, float)):
            return convert_number_to_date(value)

        # 4. Обработка текстовых представлений
        return parse_text_date(str_value)

    def convert_number_to_date(number):
        """Преобразует числа в даты"""
        try:
            # Excel serial date (1 = 1900-01-01)
            if number > 59:  # Коррекция для ошибки Excel с 1900-02-29
                number -= 1
            base_date = datetime(1899, 12, 30)
            return base_date + pd.Timedelta(days=number)
        except:
            pass

        try:
            # Unix timestamp (секунды или миллисекунды)
            if number > 10000000000:  # миллисекунды
                number = number / 1000
            return datetime.fromtimestamp(number)
        except:
            pass

        return None

    def parse_text_date(text):
        """Парсит текстовые представления дат"""
        text = text.lower().strip()

        # Словари для преобразования
        months_ru = {
            'январь': 1, 'янв': 1, 'january': 1, 'jan': 1,
            'февраль': 2, 'фев': 2, 'february': 2, 'feb': 2,
            'март': 3, 'мар': 3, 'march': 3, 'mar': 3,
            'апрель': 4, 'апр': 4, 'april': 4, 'apr': 4,
            'май': 5, 'may': 5,
            'июнь': 6, 'июн': 6, 'june': 6, 'jun': 6,
            'июль': 7, 'июл': 7, 'july': 7, 'jul': 7,
            'август': 8, 'авг': 8, 'august': 8, 'aug': 8,
            'сентябрь': 9, 'сен': 9, 'september': 9, 'sep': 9,
            'октябрь': 10, 'окт': 10, 'october': 10, 'oct': 10,
            'ноябрь': 11, 'ноя': 11, 'november': 11, 'nov': 11,
            'декабрь': 12, 'дек': 12, 'december': 12, 'dec': 12
        }

        days_ru = {
            'понедельник': 1, 'вторник': 2, 'среда': 3, 'четверг': 4,
            'пятница': 5, 'суббота': 6, 'воскресенье': 7
        }

        # Регулярные выражения для различных форматов
        patterns = [
            # DD.MM.YYYY или DD/MM/YYYY
            (r'(\d{1,2})[\.\/](\d{1,2})[\.\/](\d{4})', lambda m: datetime(int(m[3]), int(m[2]), int(m[1]))),
            # YYYY-MM-DD
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: datetime(int(m[1]), int(m[2]), int(m[3]))),
            # Месяц на русском/английском
            (r'(\d{1,2})\s+([а-яa-z]+)\s+(\d{4})',
             lambda m: datetime(int(m[3]), months_ru.get(m[2].lower(), 1), int(m[1]))),
            # Только год
            (r'(\d{4})', lambda m: datetime(int(m[1]), 1, 1)),
            # Кварталы
            (r'q([1-4])[\s\-]?(\d{4})', lambda m: datetime(int(m[2]), (int(m[1]) - 1) * 3 + 1, 1)),
            # "Сегодня", "Вчера" и т.д.
            (r'сегодня', lambda m: datetime.now()),
            (r'вчера', lambda m: datetime.now().replace(day=datetime.now().day - 1)),
            (r'позавчера', lambda m: datetime.now().replace(day=datetime.now().day - 2)),
        ]

        # Пробуем шаблоны
        for pattern, converter in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return converter(match)
                except:
                    continue

        # Обработка относительных дат
        relative_patterns = [
            (r'(\d+)\s+день', lambda m: datetime.now().replace(day=datetime.now().day - int(m[1]))),
            (r'(\d+)\s+месяц', lambda m: datetime.now().replace(month=datetime.now().month - int(m[1]))),
            (r'(\d+)\s+год', lambda m: datetime.now().replace(year=datetime.now().year - int(m[1]))),
            (r'на\s+этой\s+неделе', lambda m: datetime.now()),
            (r'на\s+прошлой\s+неделе', lambda m: datetime.now().replace(day=datetime.now().day - 7)),
        ]

        for pattern, converter in relative_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return converter(match)
                except:
                    continue

        return None

    def parse_complex_date_text(text):
        """Обработка сложных текстовых описаний дат"""
        text = text.lower()

        # "Конец месяца", "Начало года" и т.д.
        if 'конец месяца' in text or 'end of month' in text:
            today = datetime.now()
            return datetime(today.year, today.month, 1) + pd.offsets.MonthEnd(1)

        if 'начало месяца' in text or 'start of month' in text:
            today = datetime.now()
            return datetime(today.year, today.month, 1)

        if 'конец года' in text or 'end of year' in text:
            today = datetime.now()
            return datetime(today.year, 12, 31)

        if 'начало года' in text or 'start of year' in text:
            today = datetime.now()
            return datetime(today.year, 1, 1)

        # "Следующий понедельник", "Прошлая пятница"
        days_map = {'понедельник': 0, 'вторник': 1, 'среду': 2, 'четверг': 3,
                    'пятницу': 4, 'субботу': 5, 'воскресенье': 6}

        for day_ru, day_num in days_map.items():
            if f'следующий {day_ru}' in text:
                today = datetime.now()
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return today + pd.Timedelta(days=days_ahead)

            if f'прошлый {day_ru}' in text:
                today = datetime.now()
                days_before = today.weekday() - day_num
                if days_before <= 0:
                    days_before += 7
                return today - pd.Timedelta(days=days_before)

        return None

    """-------------------------------------------------------------------------------------"""
    # функции для парсинга даты публикации с листа "Каталог статей"
    def date_check(book):
        sheet = book['Каталог статей']
        list_date_states = []
        problematic_cells = []
        for i in range(2, sheet.max_row + 1):
            cell_value = sheet[f'D{i}'].value

            if cell_value is None:
                continue

            # Пробуем основные методы преобразования
            date_obj = smart_date_converter(cell_value)

            if not date_obj:
                # Пробуем дополнительные методы для сложных случаев
                date_obj = parse_complex_date_text(str(cell_value))

            if date_obj:
                list_date_states.append(date_obj)
            else:
                problematic_cells.append((i, cell_value))
                logging.warning(f"Проблемная ячейка D{i}: '{cell_value}'")

            # Вывод отчета о проблемных ячейках
        if problematic_cells:
            print(f"\nНе удалось преобразовать {len(problematic_cells)} ячеек:")
            for row, value in problematic_cells:
                print(f"Строка {row}: '{value}'")

        return list_date_states

    # функции для парсинга названия статьи с листа "Каталог статей"
    def name_check(book):
        sheet = book['Каталог статей']
        for i in range(2, len(a) + 1):
            if sheet['D' + str(i)].value is not None and sheet['C' + str(i)].value is not None and sheet[
                'B' + str(i)].value is not None:
                list_name_state = sheet['B' + str(i)].value
                list_name_states.append(list_name_state)
        return list_name_states

    # функции для парсинга даты создания с листа "Каталог статей"
    def make_check(book):
        sheet = book['Каталог статей']
        problematic_cells = []

        for i in range(2, sheet.max_row + 1):
            cell_value = sheet[f'C{i}'].value

            if cell_value is None:
                continue

            # Пробуем основные методы преобразования
            date_obj = smart_date_converter(cell_value)

            if not date_obj:
                # Пробуем дополнительные методы для сложных случаев
                date_obj = parse_complex_date_text(str(cell_value))

            if date_obj:
                list_make_states.append(date_obj)
            else:
                problematic_cells.append((i, cell_value))
                logging.warning(f"Проблемная ячейка D{i}: '{cell_value}'")

            # Вывод отчета о проблемных ячейках
        if problematic_cells:
            print(f"\nНе удалось преобразовать {len(problematic_cells)} ячеек:")
            for row, value in problematic_cells:
                print(f"Строка {row}: '{value}'")

        return list_make_states

    # Функция для определения сегодняшней даты
    def get_todays_date():
        today = datetime.datetime.today()
        return today.strftime("%Y-%m-%d")

    # Функция определения разницы между сегодняшней датой и даты из списка
    def compare_dates():
        date1 = datetime.datetime.strptime(x, "%Y-%m-%d")
        for i in range(len(DATA)):
            date2 = DATA[i]
            if 0 < (date2 - date1).days <= 180:
                date_2_list.append(date2)
        return date_2_list

    # Проверяем, есть ли статьи по данным датам публикации
    def state_function(checking, dict_date_name_state):
        search_state = []  # Не забудьте инициализировать list здесь
        for dic in checking:
            for k, v in dict_date_name_state.items():
                if v == dic:  # Сравниваем значение в dict_date_name_state с элементом checking
                    search_state.append(k)  # Добавляем ключ из dict_date_name_state
        return search_state

    # Запускаем функцию проверки наличия даты создания в словаре по названию статей
    def make_function(state_3m):
        for i in range(0, len(state_3m)):
            if state_3m[i] in dict_make_name_state:
                dic = dict_make_name_state[state_3m[i]]
                make_state.append(dic)
        return make_state

    # Убираем повторяющиеся названия статей
    def remove_duplicates_3m(search_state):
        # Используем множество для хранения уникальных слов
        unique_state_3m = list(set(search_state))
        # Преобразуем обратно в список
        return unique_state_3m

    def publ_function(state):
        publ_state = []
        for i in range(0, len(state)):
            if state[i] in dict_date_name_state:
                dic = dict_date_name_state[state[i]]
                publ_state.append(dic)
        return publ_state
# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------ВЫПОЛНЕНИЕ ФУНКЦИЙ ДЛЯ 2 КОМАНДЫ--------------------------------------------

    warnings.filterwarnings("ignore", category=UserWarning)
    book = await DataManager.get_excel_from_yandex()

    # Считаем количество строк в файле по листу "Каталог статей"
    how_much_string(book)
    # Определяем текущую дату
    x = get_todays_date()
    # Сохраняем список дат публикации статей
    DATA = date_check(book)
    # Сохраняем названия статей
    STATE = name_check(book)
    # Сохраняем список дат создания статей
    MAKE = make_check(book)

    # Объединяем в словарь список дат публикации статей и их названия
    dict_date_name_state = dict(zip(STATE, DATA))
    # Объединяем в словарь список дат создания статей и их названия
    dict_make_name_state = dict(zip(STATE, MAKE))

    # Определяем даты публикации, относительно текущей, в диапазоне до 180 дней и сохраняем в виде списка date_2_list
    checking = compare_dates()

    # Убираем повторяющиеся даты из списка
    state_3m = remove_duplicates_3m(date_2_list)

    # Сохраняем список статей по данным датам
    check_state_in_dict_old = state_function(state_3m, dict_date_name_state)
    # Убираем повторяющиеся названия статей из списка
    check_state_in_dict = remove_duplicates_3m(check_state_in_dict_old)
    # Находим даты создания статьи по её названию
    check_make_in_dict = make_function(check_state_in_dict)

    # Находим даты публикации статьи по её названию
    check_publ_in_dict = publ_function(check_state_in_dict)

    # Переводим списки дат создания и публикации из формата date в формат datetime
    date_check_make_in_dict = [dt.date() for dt in check_make_in_dict]
    date_state_3m = [dt.date() for dt in check_publ_in_dict]
    return check_state_in_dict, date_check_make_in_dict, date_state_3m