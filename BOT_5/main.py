import logging, os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from dotenv import load_dotenv


import Yandex_disk, Function1, Function2, Graph, Upload_YD, TG_form_save, Old_state
load_dotenv()

API_TOKEN = os.getenv('TOKEN_bot')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объектов бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Обработка команды /start и вывод кнопок
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Добавить плановую статью", callback_data="add_article"),
        InlineKeyboardButton("Статус заполнения Таблицы статей", callback_data="status_states"),
        InlineKeyboardButton("Дорожная карта написания статей", callback_data="notes_states"),
        InlineKeyboardButton("Ссылка на Таблицу статей", callback_data="table_states"),
        InlineKeyboardButton("Просроченные статьи", callback_data="old_states"),
        InlineKeyboardButton("Подбор статей для цитирования", callback_data="state_states")
    )
    await message.answer("Добро пожаловать! Выберите действие ниже:", reply_markup=keyboard)

# Команда получения информации с таблицы о заполнении
@dp.callback_query_handler(lambda c: c.data == "status_states")
async def status_states_callback(callback_query: types.CallbackQuery):
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await Function1.function1()
    from Function1 import all_teg, names_state
    if all_teg:
        await bot.send_message(callback_query.from_user.id, "<b>Следующим авторам необходимо заполнить Таблицу статей:</b>" + "\n" + '\n'.join(all_teg), parse_mode='HTML')
    await bot.send_message(callback_query.from_user.id, "<b>Авторам данных статей необходимо заполнить Таблицу статей:</b>" + "\n - " + '\n - '.join(names_state), parse_mode='HTML')
    os.remove('Table_Таблица статей.xlsx')
# Команда создания дорожной карты
@dp.callback_query_handler(lambda c: c.data == "notes_states")
async def notes_states_callback(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await Function2.function2()
    from Function2 import check_state_in_dict, date_check_make_in_dict, date_state_3m
    await Graph.graf(check_state_in_dict, date_check_make_in_dict, date_state_3m)
    from Graph import buf
    os.remove('Table_Таблица статей.xlsx')
    try:
        await bot.send_photo(chat_id=chat_id, photo=buf)
        buf.close()
    except Exception as e:
        print(f"Ошибка при отправке фотографии: {e}")

# Команда отправки ссылки на таблицу с Яндекс-диска
@dp.callback_query_handler(lambda c: c.data == "table_states")
async def notes_states_callback(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
                           "<b>Ссылка на заполнение Таблицы статей:</b>" + "\n" + "https://disk.yandex.ru/i/MYnqCNHmuaALqA",
                         parse_mode='HTML')

# Команда получения информации с таблицы о просроченных статьях
@dp.callback_query_handler(lambda c: c.data == "old_states")
async def status_states_callback(callback_query: types.CallbackQuery):
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await Old_state.function_old_state()
    from Old_state import check_state_in_dict
    await bot.send_message(callback_query.from_user.id, "<b>Список просроченных статей:</b>" + "\n - " + '\n - '.join(check_state_in_dict), parse_mode='HTML')
    os.remove('Table_Таблица статей.xlsx')

# Команда для заполнения ТГ-формы
# Зададим класс для ТГ-формы
class ArticleForm(StatesGroup):
    title = State()
    date = State()
    thesis = State()
    keywords = State()
    authors = State()
@dp.callback_query_handler(lambda c: c.data == "add_article")
async def add_article_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await ArticleForm.title.set()
    await bot.send_message(callback_query.from_user.id, "Введите название статьи:")

# Обработка заполнения всех полей формы:
@dp.message_handler(state=ArticleForm.title)
async def process_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["title"] = message.text
    await ArticleForm.next()  # Переходим к следующему состоянию
    await message.reply("Введите плановую дату публикации (ДД.ММ.ГГГГ):")

@dp.message_handler(state=ArticleForm.date)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["date"] = datetime.strptime(message.text, "%d.%m.%Y")
    await ArticleForm.next()
    await message.reply("Введите тезис статьи:")

@dp.message_handler(state=ArticleForm.thesis)
async def process_thesis(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["thesis"] = message.text
    await ArticleForm.next()
    await message.reply("Введите ключевые слова:")

@dp.message_handler(state=ArticleForm.keywords)
async def process_keywords(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["keywords"] = message.text
    await ArticleForm.next()
    await message.reply("Введите имена авторов:")

@dp.message_handler(state=ArticleForm.authors)
async def process_authors(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["authors"] = message.text
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await TG_form_save.function_TG_form_save(os.getenv('SAVE_PATH'), os.getenv('SAVE_PATH'), data["title"], data["date"], data["thesis"], data["authors"], data["keywords"])
    await message.reply("Происходит запись данных")
    try:
        await Upload_YD.upload_file_to_yandex_disk(os.getenv('TOKEN'), os.getenv('SAVE_PATH'), os.getenv('DIRECTORY'))
        await message.reply("Данные успешно записаны на ЯД")
    except:
        await message.reply("Ошибка записи данных на ЯД")
    await state.finish()
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)