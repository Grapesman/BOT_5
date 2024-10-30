# Импортируем библиотеки
import os, telebot, time, threading
from dotenv import load_dotenv
load_dotenv()
import Yandex_disk, Function1, Function2, Graph
# --------------------------------------------------КОД ТГ БОТА---------------------------------------------------------
# Основной код
bot = telebot.TeleBot(os.getenv('TOKEN_bot'))
# Функция, обрабатывающая команду старт
@bot.message_handler(commands=["status"])
def start(m, res=False):
    if all_teg:
        bot.send_message(m.chat.id, "<b>Следующим авторам необходимо заполнить Таблицу статей:</b>" + "\n" + '\n'.join(all_teg), parse_mode = 'HTML')
    bot.send_message(m.chat.id, "<b>Авторам данных статей необходимо заполнить Таблицу статей:</b>" + "\n - " + '\n - '.join(names_state), parse_mode = 'HTML')

@bot.message_handler(commands=["notes"])
def send_photo_file(message):
    chat_id = message.chat.id
    try:
        bot.send_photo(chat_id=chat_id, photo=buf)
        buf.close()
    except Exception as e:
        print(f"Ошибка при отправке фотографии: {e}")
#
#------------------------------------------------------------------------------------------------------------------------

def start_bot():
    bot.polling(none_stop=True, interval=0)

# Запускаем бота в отдельном потоке
thread = threading.Thread(target=start_bot)
thread.start()
# Запускаем второй поток для парсинга
while True:
    Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    Function1.function1()
    from Function1 import all_teg, names_state
    Function2.function2()
    from Function2 import check_state_in_dict, date_check_make_in_dict, date_state_3m
    Graph.graf(check_state_in_dict, date_check_make_in_dict, date_state_3m)
    from Graph import buf
    os.remove('Table_Таблица статей.xlsx')
    time.sleep(1)  # Добавьте небольшую задержку, чтобы избежать перегрузки процессора