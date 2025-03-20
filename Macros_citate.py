from data_manager import DataManager


global word_list
global er_mes_opub
global er_mes_search
global withouht_key


async def bibliography_macros_1(data_name):
    book = await DataManager.get_excel_from_yandex()
    sheet = book['Каталог статей']
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
