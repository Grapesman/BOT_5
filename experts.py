"""Данный файл организует помощь экспертам и кураторам узнавать о своих подчиненных. Задача состоит
в том, чтобы автоматически рассылать уведомление с тегами своих подопечных вышестоящим начальникам"""
from data_manager import DataManager


async def function_experts():
    # Вводим списки
    a = []  # Запоминает количество заполненных в таблице строк на листе "Каталог статей"
    b = []  # Запоминает количество заполненных в таблице строк на листе "Community"
    list_names_input = [] # Список для сохранения значений фамилий с листа "Community"
    list_tegs_input = [] # Список для сохранения значений тегов с листа "Community"
    list_rols_input = []  # Список для сохранения значений ролей с листа "Community"
    dict_name_tegs = {} # Словарь для сохранения значений фамилий и тегов с листа "Community"
    dict_name_rols = {} # Словарь для сохранения значений фамилий и ролей с листа "Community"
    list_exp_states = []
    list_write_states = []
    list_cur_states = []
    list_for_teg_write = []
    # Функция определения количества заполненных строк. Определяем по столбцу "A" с нумерацией для листа "Каталог статей"
    def how_much_string(book):
        i = 1
        sheet = book['Каталог статей']
        while sheet['A' + str(i)].value is not None:
            a.append(i)
            i += 1
        return
    # Определим количество заполненных строк в файле по фамилиям для листа "Community"
    def how_much_string_community(book):
        i = 3
        sheet = book['Community']
        while sheet['B' + str(i)].value is not None:
            b.append(i)
            i+=1
        return
    # Функция создания словаря при парсинге Фамилий и тегов
    def make_dict(book):
        global dict_name_tegs
        sheet = book['Community']
        for i in range(3, len(b)+3):
            if sheet['B' + str(i)].value is not None and sheet['O' + str(i)].value is not None:
                list_name_input = sheet['B' + str(i)].value
                list_names_input.append(list_name_input)
                list_teg_input = sheet['O' + str(i)].value
                list_tegs_input.append(list_teg_input)
                dict_name_tegs = dict(zip(list_names_input, list_tegs_input))
        return dict_name_tegs
    # Функция создания словаря при парсинге Фамилий и ролей
    def make_dict_rol(book):
        global dict_name_rols
        sheet = book['Community']
        for i in range(3, len(b)+3):
            if sheet['B' + str(i)].value is not None and sheet['O' + str(i)].value is not None:
                list_name_input = sheet['B' + str(i)].value
                list_names_input.append(list_name_input)
                list_rol_input = sheet['D' + str(i)].value
                list_rols_input.append(list_rol_input)
                dict_name_rols = dict(zip(list_names_input, list_rols_input))
        return dict_name_rols
    # функции определения наличия требуемых параметров с листа "Каталог статей"
    def date_check1(book):
        sheet = book['Каталог статей']
        for i in range(2, len(a) + 1):
            if sheet['K' + str(i)].value != "Опубликована" and sheet['N' + str(i)].value == "Внутренее":
                list_date_state = sheet['V' + str(i)].value
                list_exp_states.append(list_date_state)
        return list_exp_states
    def date_check2(book):
        sheet = book['Каталог статей']
        for i in range(2, len(a) + 1):
            if sheet['K' + str(i)].value != "Опубликована" and sheet['N' + str(i)].value == "Внутренее":
                list_date_state = sheet['W' + str(i)].value
                list_write_states.append(list_date_state)
        return list_write_states
    def date_check3(book):
        sheet = book['Каталог статей']
        for i in range(2, len(a) + 1):
            if sheet['K' + str(i)].value != "Опубликована" and sheet['N' + str(i)].value == "Внутренее":
                list_date_state = sheet['X' + str(i)].value
                list_cur_states.append(list_date_state)
        return list_cur_states

    def search_write_function(list_exp, dict_exp_write):
        for i in range(len(list_exp)):
            list_for_teg_write.append(list_exp[i])
            if list_exp[i] in dict_exp_write:
                dic = dict_exp_write[list_exp[i]]
                list_for_teg_write.append(dic)



# ------------------------------------------ВЫПОЛНЕНИЕ ФУНКЦИЙ ДЛЯ КОМАНДЫ--------------------------------------------

    book = await DataManager.get_excel_from_yandex()

    # Считаем количество строк в файле по листу "Каталог статей"
    how_much_string(book)
    # Считаем количество строк в файле по листу "Community"
    how_much_string_community(book)

    # Формируем словарь с фамилиями и тегами с листа "Community"
    data_dict = make_dict(book)
    # Формируем словарь с фамилиями и ролями с листа "Community"
    rol_dict = make_dict_rol(book)
    # Формируем словарь с фамилиями экспертов с листа "каталог статей"
    list_exp = date_check1(book)
    # Формируем словарь с фамилиями написание с листа "каталог статей"
    list_write = date_check2(book)
    # Формируем словарь с фамилиями кураторов с листа "каталог статей"
    list_cur = date_check3(book)
    # Словарь эксперт-написание
    dict_exp_write = dict(zip(list_exp, list_write))
    # Словарь куратор-написание
    dict_exp_write = dict(zip(list_cur, list_write))
    list_exp_states_uniq = list(set(list_exp)) #Оставляем фамилии экспертов без повторов
    list_cur_states_uniq = list(set(list_cur)) #Оставляем фамилии кураторов без повторов
    # Определяем длину списков без повторов экспертов
    len_list_exp_states_uniq = len(list_exp_states_uniq)
    # Определяем длину списков без повторов кураторов
    len_list_cur_states_uniq = len(list_cur_states_uniq)

    print(list_cur_states_uniq)
    print(list_exp_states_uniq)



