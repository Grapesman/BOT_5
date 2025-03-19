from openpyxl import load_workbook
global a
async def how_much_string(file_path):
    global a
    a = []
    i = 1
    book = load_workbook(filename = file_path)
    sheet = book['Каталог статей']
    while sheet['A' + str(i)].value is not None:
        a.append(i)
        i+=1
    return a