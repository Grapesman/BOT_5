import logging, os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from dotenv import load_dotenv
import Yandex_disk, Function1, Function2, Graph
load_dotenv()

API_TOKEN = os.getenv('TOKEN_bot')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объектов бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['status'])
async def send_welcome(message: types.Message):
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await Function1.function1()
    from Function1 import all_teg, names_state
    if all_teg:
        await message.answer("<b>Следующим авторам необходимо заполнить Таблицу статей:</b>" + "\n" + '\n'.join(all_teg), parse_mode='HTML')
    await message.answer("<b>Авторам данных статей необходимо заполнить Таблицу статей:</b>" + "\n - " + '\n - '.join(names_state), parse_mode='HTML')
    os.remove('Table_Таблица статей.xlsx')

@dp.message_handler(commands=["notes"])
async def send_photo_file(message):
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await Function2.function2()
    from Function2 import check_state_in_dict, date_check_make_in_dict, date_state_3m
    await Graph.graf(check_state_in_dict, date_check_make_in_dict, date_state_3m)
    from Graph import buf
    os.remove('Table_Таблица статей.xlsx')
    chat_id = message.chat.id
    try:
        await bot.send_photo(chat_id=chat_id, photo=buf)
        buf.close()
    except Exception as e:
        print(f"Ошибка при отправке фотографии: {e}")
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)