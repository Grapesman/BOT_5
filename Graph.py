import matplotlib.pyplot as plt
import pandas as pd
import datetime
import io
from matplotlib.dates import DateFormatter, MonthLocator

global buf


async def graf(check_state_in_dict, date_check_make_in_dict, date_state_3m):
    global buf

    # Создаем датафрейм для построения графика
    data = {
        'Категория': check_state_in_dict,
        'Начальная дата': date_check_make_in_dict,
        'Конечная дата': date_state_3m,
    }

    # Конвертируем данные в DataFrame
    df = pd.DataFrame(data)

    # Преобразуем даты в datetime
    df['Начальная дата'] = pd.to_datetime(df['Начальная дата'])
    df['Конечная дата'] = pd.to_datetime(df['Конечная дата'])

    # Рассчитываем длину каждого столбца диаграммы
    df['Длительность'] = df['Конечная дата'] - df['Начальная дата']

    # Определяем временной диапазон для графика
    all_start_dates = df['Начальная дата'].min()
    all_end_dates = df['Конечная дата'].max()

    # Добавляем отступы по краям (10% от общего диапазона)
    total_range = (all_end_dates - all_start_dates).days
    padding = max(total_range * 0.1, 30)  # минимум 30 дней отступ

    start_date_for_diagr = all_start_dates - pd.Timedelta(days=padding)
    end_date_for_diagr = all_end_dates + pd.Timedelta(days=padding)

    # Убедимся, что сегодняшняя дата включена в диапазон
    today = datetime.datetime.now()
    if today < start_date_for_diagr:
        start_date_for_diagr = today - pd.Timedelta(days=30)
    if today > end_date_for_diagr:
        end_date_for_diagr = today + pd.Timedelta(days=30)

    plt.ion()
    # Формируем график
    fig, ax = plt.subplots(figsize=(12, 8))

    # Устанавливаем длину столбца Игрек (названия статей)
    y_positions = range(len(df))

    # Строим столбцы с использованием matplotlib dates
    for i in range(len(df)):
        start_date = df['Начальная дата'].iloc[i]
        duration_days = df['Длительность'].iloc[i].days

        # Преобразуем в числовой формат для matplotlib
        start_num = start_date.toordinal()
        duration_num = duration_days

        ax.barh(y_positions[i], duration_num, left=start_num,
                align='center', color='lightblue', alpha=0.7)

    # Добавление линии сегодняшней даты
    today_num = today.toordinal()
    ax.axvline(today_num, color='red', linestyle='--', linewidth=2, label='Сегодня')

    # Обрезаем названия статей до 50 символов
    def truncate(text):
        if isinstance(text, str):
            return text[:50] + '...' if len(text) > 50 else text
        return str(text)

    dfack = df['Категория'].apply(truncate)

    # Настройка осей
    ax.set_yticks(y_positions)
    ax.set_yticklabels(dfack, fontsize=8)
    plt.title('ДК написания статей', pad=20, fontsize=14)

    # НАСТРОЙКА ОСИ X ДЛЯ РАВНОМЕРНОГО ОТОБРАЖЕНИЯ ДАТ
    # Устанавливаем пределы оси X
    ax.set_xlim(start_date_for_diagr.toordinal(), end_date_for_diagr.toordinal())

    # Создаем равномерно распределенные даты для оси X
    date_range = pd.date_range(start=start_date_for_diagr, end=end_date_for_diagr, freq='MS')  # Start of Month

    # Если диапазон слишком мал, используем более частые деления
    if len(date_range) < 3:
        date_range = pd.date_range(start=start_date_for_diagr, end=end_date_for_diagr, freq='2W')
    if len(date_range) < 3:
        date_range = pd.date_range(start=start_date_for_diagr, end=end_date_for_diagr, freq='1W')

    # Устанавливаем деления и подписи
    ax.set_xticks([d.toordinal() for d in date_range])
    ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in date_range],
                       rotation=45, fontsize=7, ha='right')

    # Альтернативный вариант: автоматическое определение оптимального количества делений
    def set_optimal_xticks(ax, start_date, end_date):
        """Автоматически устанавливает оптимальное количество делений на оси X"""
        total_days = (end_date - start_date).days

        if total_days <= 30:
            freq = '1W'  # неделя
        elif total_days <= 90:
            freq = '2W'  # 2 недели
        elif total_days <= 180:
            freq = '1M'  # месяц
        elif total_days <= 365:
            freq = '2M'  # 2 месяца
        else:
            freq = '3M'  # 3 месяца

        date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
        ax.set_xticks([d.toordinal() for d in date_range])
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in date_range],
                           rotation=45, fontsize=7, ha='right')

    # Используем автоматическую настройку
    set_optimal_xticks(ax, start_date_for_diagr, end_date_for_diagr)

    # Настройка внешнего вида
    plt.legend(loc='upper left', fontsize=8)
    plt.grid(True, alpha=0.3)

    # Убедимся, что все элементы помещаются
    plt.tight_layout()

    # Сохранение графика в памяти
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf