# --------------------------------------------------КОД ТГ БОТА---------------------------------------------------------
import telebot
def bot(TOKEN_bot, all_teg, names_state):
    # Основной код
    bot = telebot.TeleBot(TOKEN_bot)
    # Функция, обрабатывающая команду "status"
    @bot.message_handler(commands=["status"])
    def start(m, res=False):
        if all_teg:
            bot.send_message(m.chat.id, "<b>Следующим авторам необходимо заполнить Таблицу статей:</b>" + "\n" + '\n'.join(all_teg), parse_mode = 'HTML')
        bot.send_message(m.chat.id, "*Авторам данных статей необходимо заполнить Таблицу статей:*" + "\n - " + '\n - '.join(names_state), parse_mode = 'Markdown')
    # Функция, обрабатывающая команду "notes"
    @bot.message_handler(commands=["notes"])
    def send_photo_file(message):
        chat_id = message.chat.id
        img = 'plot.jpg'
        try:
            with open(img, 'rb') as file:
                bot.send_photo(chat_id, file)
        except Exception as e:
            print(f"Ошибка при отправке фотографии: {e}")
    #Запускаем бота
    bot.polling(none_stop=True, interval=0)
# ----------------------------------------------------------------------------------------------------------------------
