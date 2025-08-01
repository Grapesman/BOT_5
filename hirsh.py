from data_manager import DataManager
data_dict = 0
async def hirsh_function():
    global data_dict
    b = []
    list_hirsh = []
    def how_much_string_community(book):
        i = 3
        sheet = book['Community']
        while sheet['B' + str(i)].value is not None:
            b.append(i)
            i += 1
        return
        # Функция создания словаря при парсинге Фамилий и тегов
    def make_dict(book):
        sheet = book['Community']
        for i in range(3, len(b)+3):
            if sheet['K' + str(i)].value is not None and sheet['K' + str(i)].value >= 2:
                hirsh = sheet['B' + str(i)].value
                list_hirsh.append(hirsh)
        return len(list_hirsh)

    book = await DataManager.get_excel_from_yandex()

    # Считаем количество строк в файле по листу "Community"
    how_much_string_community(book)

    # Формируем словарь с фамилиями и тегами с листа "Community"
    data_dict = make_dict(book)

