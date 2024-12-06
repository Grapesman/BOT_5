import matplotlib.pyplot as plt
import pandas as pd
import datetime, io
global buf
async def graf(check_state_in_dict, date_check_make_in_dict, date_state_3m):
    # Создаем датафрейм для построения графика
    global buf
    data = {
        'Категория': check_state_in_dict,
        'Начальная дата': date_check_make_in_dict,
        'Конечная дата': date_state_3m,
    }

    # Конвертируем данные в DataFrame
    df = pd.DataFrame(data)

    # Рассчитываем длину каждого столбца диаграммы
    df['Длительность'] = pd.to_datetime(df['Конечная дата']) - pd.to_datetime(df['Начальная дата'])
    plt.ion()
    # Формируем график
    fig, ax = plt.subplots()
    # Снова определяем текущую дату для построения на диаграмме сегодняшней линии
    today = datetime.datetime.now()

    # Устанавливаем длину столбца Игрек (названия статей)
    y_positions = range(len(df))
    # Рассчитываем значения оси дат (Икс)
    start_date_for_diagr = datetime.datetime.today() - datetime.timedelta(days=365)
    aaa = start_date_for_diagr.strftime('%Y-%m-%d')
    end_date_for_diagr = today + datetime.timedelta(days=180)
    bbb = end_date_for_diagr.strftime('%Y-%m-%d')

    # Строим столбцы
    for i in range(len(df)):
        start_date = df['Начальная дата'][i]
        duration_days = df['Длительность'][i].days
        ax.barh(y_positions[i], duration_days, left=(start_date - start_date_for_diagr.date()).days,
                align='center',
                color='lightblue')

    # Добавление линии сегодняшней даты
    today_line = datetime.date.today()
    today_position = (today_line - start_date_for_diagr.date()).days
    ax.axvline(today_position, color='red', linestyle='--', label='Сегодня')

    # Обрезаем названия статей до 50 символов
    def truncate(text):
        if isinstance(text, str):  # Проверяем, является ли элемент строкой
            return text[:50]  # Обрезаем до 50 символов
        return text  # Если это не строка, возвращаем как есть

    # Применяем функцию к элементу 'Категория' в DataFrame
    dfack = df['Категория'].apply(truncate)

    # Настройка осей
    ax.set_yticks(y_positions)
    ax.set_yticklabels(dfack, fontsize=6)
    plt.title('ДК написания статей', pad=10, x=-0.4, y=1.0, fontsize=12)

    # Настраиваем ось X для отображения дат
    xticks = pd.date_range(start=aaa, end=bbb, freq='1M')
    ax.set_xticks((xticks - start_date_for_diagr).days)
    ax.set_xticklabels(xticks.strftime('%Y-%m-%d'), rotation=90, fontsize=6)
    # Вывод графика
    plt.legend(loc='lower left', fontsize=6)
    plt.grid()
    plt.tight_layout()
    # Сохранение графика в памяти (в буфер)
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg')
    buf.seek(0)  # Перемещаемся в начало буфера
    plt.close()  # Закрываем фигуру, чтобы избежать отображения графика
    return buf