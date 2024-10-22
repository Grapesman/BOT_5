Совокупность файлов обеспечивает парсинг Excel-файла, находящегося на Яндекс-диске и выводит необходимую информацию.
1. Главным для запуска является файл main.py, в него подключены остальные файлы
2. При запуске файла main.py изначально вызывается файл Yandex_disk и выполняется функция по загрузке Excel-файла с Яндекс-диска
3. Затем за счет функций в файле Functions.py происходит поиск необходимых условий для их вывода. Условия описаны комментариями в коде файла main.py 
    3.1 Изначально происходит подсчет заполненных строк по определенным столбцам в Excel-файле
    3.2 Затем происходит сохранение в виде списков требуемых значений
    3.3 После формирование их в словари
    3.4 По требуемым условиям, значения величин сопоставляются со словарями, находятся ключи и выводится значения
4. Аналогично происходит поиск и сохранение требуемых величин для второго условия
5. Затем вызывается файл Graph.py с его функцией для создания графика и его сохранения
6. В итоге вызывается файл Telegram.py с функцией запуска телеграм-бота и выводом требуемых значений