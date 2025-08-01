"""Анализ пользы сообщества, данная функция будет формировать данные о количестве опубликованных и процитированных статей"""
# создаем счетчик опубликованных статей за данный квартал
# 1-й квартал - 01.01 - 31.03 (рассылка 1.04)
# 2-й квартал - 01.04 - 31.06 (рассылка 1.07)
# 3-й квартал - 01.07 - 31.09 (рассылка 1.10)
# 4-й квартал - 01.10 - 31.12 (рассылка 1.01)
import datetime
import warnings
from data_manager import DataManager

how_much_ratingQ1 = None
how_much_ratingQ2 = None
how_much_ratingQ3 = None
how_much_ratingQ4 = None
how_much_ratingCP = None
how_much_ratingVAK = None
how_much_ratingRINC = None

checking = None
last_checking = None
cit_now = None
cit_last = None
async def function_statistic():
    a = []
    list_date_states = []  # Список для парсинга дат публикации статей с листа "Каталог статей"
    date_list = []
    list_raiting_states = []
    list_name_states = []  # Список для парсинга названий статей с листа "Каталог статей"
    list_key_states = []
    dat_filt_now = []
    dat_filt_last = []
    make_state = []

    # --------------------------------------------------ФУНКЦИИ КОМАНДЫ---------------------------------------------------
    global checking
    global last_checking
    global cit_now
    global cit_last

    global how_much_ratingQ1
    global how_much_ratingQ2
    global how_much_ratingQ3
    global how_much_ratingQ4
    global how_much_ratingCP
    global how_much_ratingVAK
    global how_much_ratingRINC
    # Функция определения количества заполненных строк. Определяем по столбцу "A" с нумерацией для листа "Каталог статей"
    def how_much_string(book):
        i = 1
        sheet = book['Каталог статей']
        while sheet['A' + str(i)].value is not None:
            a.append(i)
            i += 1
        return

    # функции определения наличия требуемых параметров с листа "Каталог статей"
    def date_check(book):
        sheet = book['Каталог статей']
        for i in range(2, len(a) + 1):
            if sheet['D' + str(i)].value is not None and sheet['C' + str(i)].value is not None and sheet[
                'B' + str(i)].value is not None and sheet['K' + str(i)].value == "Опубликована" and sheet['J' + str(i)].value is not None:
                list_date_state = sheet['D' + str(i)].value
                list_date_states.append(list_date_state)
        return list_date_states

    # Функция для определения сегодняшней даты
    def get_todays_date():
        today = datetime.datetime.today()
        return today.strftime("%Y-%m-%d")

    # Функция определения количества опубликованных статей за текущие 3 месяца
    def compare_dates(x, DATA):
        how_much_date_publ_now = 0
        date1 = datetime.datetime.strptime(x, "%Y-%m-%d")
        for i in range(len(DATA)):
            date2 = DATA[i]
            if 0 < (date1 - date2).days <= 90:
                how_much_date_publ_now+=1
        return how_much_date_publ_now

    # Функция определения количества опубликованных статей за прошлые 3 месяца
    def last_m_publ_state(x, DATA):
        how_much_date_publ_last_m = 0
        date1 = datetime.datetime.strptime(x, "%Y-%m-%d")
        # Определяем "сегодня" 1 квартал назад
        date_minus_30 = date1 - datetime.timedelta(days=90)
        for i in range(len(DATA)):
            date2 = DATA[i]
            if 0 < (date_minus_30 - date2).days <= 90:
                how_much_date_publ_last_m += 1
        return how_much_date_publ_last_m
#_____________________________Определение количества цитирований____________________________________________________
    # функции для парсинга названия статьи с листа "Каталог статей"
    def name_check(book):
        sheet = book['Каталог статей']
        for i in range(2, len(a) + 1):
            if sheet['D' + str(i)].value is not None and sheet['C' + str(i)].value is not None and sheet['B' + str(i)].value is not None and sheet['J' + str(i)].value is not None and sheet['K' + str(i)].value == "Опубликована":
                list_name_state = sheet['B' + str(i)].value
                list_name_states.append(list_name_state)
        return list_name_states

    # функции для парсинга ключевых слов с листа "Каталог статей"
    def key_check(book):
        sheet = book['Каталог статей']
        for i in range(2, len(a) + 1):
            if sheet['D' + str(i)].value is not None and sheet['C' + str(i)].value is not None and sheet[
                'B' + str(i)].value is not None and sheet['J' + str(i)].value is not None and sheet['K' + str(i)].value == "Опубликована":
                list_date_state = sheet['J' + str(i)].value
                list_key_states.append(list_date_state)
        return list_key_states

    # функция для парсинга рейтинга журналов с листа "Каталог статей"
    def rating_check(book):
        sheet = book['Каталог статей']
        for i in range(2, len(a) + 1):
            if sheet['D' + str(i)].value is not None and sheet['C' + str(i)].value is not None and sheet[
                'B' + str(i)].value is not None and sheet['J' + str(i)].value is not None and sheet['K' + str(i)].value == "Опубликована":
                list_raiting_state = sheet['M' + str(i)].value
                list_raiting_states.append(list_raiting_state)
        return list_raiting_states

    def filter_dates_last_90_days(DATA):
        date1 = datetime.datetime.strptime(x, "%Y-%m-%d")
        for i in range(len(DATA)):
            date2 = DATA[i]
            if 0 < (date1 - date2).days <= 90:
                dat_filt_now.append(date2)
        return dat_filt_now
    def filter_dates_last_180_days(DATA):
        date1 = datetime.datetime.strptime(x, "%Y-%m-%d")
        # Определяем "сегодня" 1 квартал назад
        date_minus_30 = date1 - datetime.timedelta(days=90)
        for i in range(len(DATA)):
            date2 = DATA[i]
            if 0 < (date_minus_30 - date2).days <= 90:
                dat_filt_last.append(date2)
        return dat_filt_last

    def state_function(checking, dict_date_name_state):
        search_state = []  # Не забудьте инициализировать list здесь
        for dic in checking:
            for k, v in dict_date_name_state.items():
                if v == dic:  # Сравниваем значение в dict_date_name_state с элементом checking
                    search_state.append(k)  # Добавляем ключ из dict_date_name_state
        return search_state
    def make_function(state_3m):
        for i in range(0, len(state_3m)):
            if state_3m[i] in dict_key_name_state:
                dic = dict_key_name_state[state_3m[i]]
                make_state.append(dic)
        return make_state

    # Поиск количества статей с определенным рейтингом:
    def raiting_func_searchQ1(list):
        counterQ1 = 0
        for i in range(0, len(list)):
            if list[i] == "Q1":
                counterQ1 =+ 1
        return counterQ1
    def raiting_func_searchQ2(list):
        counterQ2 = 0
        for i in range(0, len(list)):
            if list[i] == "Q2":
                counterQ2 =+ 1
        return counterQ2

    def raiting_func_searchQ3(list):
        counterQ3 = 0
        for i in range(0, len(list)):
            if list[i] == "Q3":
                counterQ3 =+ 1
        return counterQ3
    def raiting_func_searchQ4(list):
        counterQ4 = 0
        for i in range(0, len(list)):
            if list[i] == "Q4":
                counterQ4 =+ 1
        return counterQ4

    def raiting_func_searchCP(list):
        counterCP = 0
        for i in range(0, len(list)):
            if list[i] == "Conference paper":
                counterCP =+ 1
        return counterCP
    def raiting_func_searchVAK(list):
        counterVAK = 0
        for i in range(0, len(list)):
            if list[i] == "ВАК":
                counterVAK =+ 1
        return counterVAK
    def raiting_func_searchRINC(list):
        counterRINC = 0
        for i in range(0, len(list)):
            if list[i] == "РИНЦ":
                counterRINC =+ 1
        return counterRINC


    def search_citate_state(spisok, book):
        b = 0
        all_b = 0
        for i in range(len(spisok)):
            sheet = book['Каталог статей']
            data_name = spisok[i]
            start_row = 2
            last_row = sheet.max_row
            num_row = None  # Инициализируем переменную num_row
            global er_mes_opub
            global er_mes_search
            global withouht_key
            er_mes_search = False
            er_mes_opub = False
            withouht_key = False

            def find_words_in_excel(words_list, num_row):
                found_rows = []
                # Проходим по всем ячейкам в колонке "J"
                for row in range(2, sheet.max_row + 1):
                    cell_value = sheet[f'J{row}'].value
                    if cell_value:  # Проверяем, что ячейка не пустая
                        for word in words_list:
                            if word in str(cell_value):  # Приводим к строке и проверяем наличие слова
                                found_rows.append(sheet[f"B{row}"].value)  # Сохраняем название
                                break  # Если нашли слово, переходим к следующей ячейке

                # Перед удалением проверяем, существует ли элемент в списке
                value_to_remove = sheet[f"B{num_row}"].value
                if value_to_remove in found_rows:
                    found_rows.remove(value_to_remove)
                return found_rows

            def split_string_by_commas(input_string):
                # Разделяем строку по запятым и удаляем лишние пробелы
                result_list = [item.strip() for item in input_string.split(',')]
                return result_list

            for i in range(start_row, last_row + 1):
                if sheet[f"B{i}"].value == data_name:
                    num_row = i
                    print("Статья найдена")
                    break  # Если нашли, выходим из цикла

            if num_row is None:
                print("Статья не найдена")
                er_mes_search = True
                return

            if sheet[f"K{num_row}"].value == "Опубликована":
                er_mes_opub = True
            else:
                # Запишем ключи данной статьи
                list_key = sheet[f"J{num_row}"].value
                if list_key:
                    result_key = split_string_by_commas(list_key)
                    global word_list
                    word_list_old = find_words_in_excel(result_key, num_row)
                    word_list = word_list_old[:7]


                else:
                    word_list = None
                    withouht_key = True
                    print("Список ключевых слов у данной статьи отсутствует")

            if er_mes_search:
                b = 0
            elif er_mes_opub:
                b = 0
            else:
                if word_list:
                    b = len(word_list)
            all_b+=b
        return all_b
    # ------------------------------------------ВЫПОЛНЕНИЕ ФУНКЦИЙ --------------------------------------------

    warnings.filterwarnings("ignore", category=UserWarning)
    book = await DataManager.get_excel_from_yandex()

    # Считаем количество строк в файле по листу "Каталог статей"
    how_much_string(book)
    # Определяем текущую дату
    x = get_todays_date()
    # Сохраняем список дат публикации всех статей
    DATA = date_check(book)
    # Определяем даты публикации, относительно текущей, в диапазоне до 90 дней и сохраняем в виде списка date_2_list
    checking = compare_dates(x, DATA)
    # Аналогично для предыдущего месяца
    last_checking = last_m_publ_state(x, DATA)
    #___________________________________________________________________________________________________
    # Парсим названия статей все
    name_state = (name_check(book))
    # Парсим список ключевых слов
    key_state = key_check(book)
    # Парсим список рейтинга журналов
    raiting_state = rating_check(book)
    # Объединяем в словарь список дат публикации статей и их названия
    dict_date_name_state = dict(zip(name_state, DATA))
    # Объединяем в словарь список ключ слов статей и их названия
    dict_key_name_state = dict(zip(name_state, key_state))
    # Объединяем в словарь список рейтинга статей и их названия
    dict_raiting_name_state = dict(zip(raiting_state, name_state))

    #Отбираем даты в диапазоне 90 дней от сегодня текущего
    date_filters_now = filter_dates_last_90_days(DATA)
    #Отбираем даты в диапазоне 90 дней от сегодня прошлого
    date_filters_last = filter_dates_last_180_days(DATA)
    # Находим названия статей за текущие 90 дней
    check_dict_name_date_now = state_function(date_filters_now, dict_date_name_state)
    # Находим названия статей за прошлые 90 дней
    check_dict_name_date_last = state_function(date_filters_last, dict_date_name_state)

    # Находим рейтинги опубликованных статей за 90 дней
    check_dict_name_rainting_now = state_function(check_dict_name_date_now, dict_raiting_name_state)
    how_much_ratingQ1 = raiting_func_searchQ1(check_dict_name_rainting_now)
    how_much_ratingQ2 = raiting_func_searchQ2(check_dict_name_rainting_now)
    how_much_ratingQ3 = raiting_func_searchQ3(check_dict_name_rainting_now)
    how_much_ratingQ4 = raiting_func_searchQ4(check_dict_name_rainting_now)
    how_much_ratingCP = raiting_func_searchCP(check_dict_name_rainting_now)
    how_much_ratingVAK = raiting_func_searchVAK(check_dict_name_rainting_now)
    how_much_ratingRINC = raiting_func_searchRINC(check_dict_name_rainting_now)

    # Находим список ключ слов по названию текущ статей
    #check_dict_name_key_now = make_function(check_dict_name_date_now)
    # Находим список ключ слов по названию прошлых статей
    #check_dict_name_key_last = make_function(check_dict_name_date_last)
    #Кол-во процитированных статей текущ
    cit_now = search_citate_state(check_dict_name_date_now, book)
    #Кол-во процитированных статей прошл
    cit_last = search_citate_state(check_dict_name_date_last, book)
