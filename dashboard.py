import matplotlib.pyplot as plt
import numpy as np

procent = 75
Kolich_state = 12
Top_5 = ["Иванов И.А.", "Петров А.В.", "Сидоров А.К.", "Соловьев А.П.", "Соколов А.Г."]
Hirsh_last = 5
Hirsh_now = 7
# Построение кольцевой диаграммы (Проценты выполненных задач за квартал)
def draw_ring_chart(percentage):
    plt.figure(figsize=(8, 5))

    # Проверяем, что значение в пределах 0-100
    if not (0 <= percentage <= 100):
        raise ValueError("Percentage should be between 0 and 100")
    # Вычисляем оставшийся процент
    remaining_percentage = 100 - percentage
    # Данные для построения диаграммы
    sizes = [remaining_percentage, percentage]
    # Указываем, что нужно создать круговую диаграмму (пирог) с равномерными дисками
    wedges, autotexts = plt.pie(sizes, startangle=90,
                                       wedgeprops=dict(edgecolor='w'))
    # Превращаем круговую диаграмму в кольцевую
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.subplots_adjust(bottom=0.1, left=-0.3)
    # Установка значения в середине
    center_value = f"{percentage}%"
    plt.text(0, 0, str(center_value), ha='center', va='center', fontsize=20, color='black')
    # Изменяем оси для равных значений
    plt.axis('equal')
    # Заголовок диаграммы
    plt.title("Выполнение задач")

    # Количество написанных статей
    plt.text(0.5, 0.5, 'Количество написанных статей'+'\n'+ str(Kolich_state) )
    # ТОП 5 по статьям
    plt.text(0.7, 0.7, 'ТОП 5 сотрудников по количеству статей'+'\n'+ '\n'.join(Top_5))
    # Показываем диаграмму
    plt.show()
draw_ring_chart(procent)

