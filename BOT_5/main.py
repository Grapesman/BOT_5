import logging, os
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from datetime import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from dotenv import load_dotenv
from Keyboard import keyboard
import Yandex_disk, Function1, Function2, Graph, Upload_YD, TG_form_save, Old_state, Macros_citate
load_dotenv()

API_TOKEN = os.getenv('TOKEN_bot')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объектов бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(dp):
    await bot.send_message(chat_id= "-1002072987116", text = "БОТ П5 активен.")
    await bot.send_message(chat_id= "-1002072987116", text = "Добро пожаловать, выберете действие ниже.", reply_markup=keyboard)

async def on_shutdown(dp):
    await bot.send_message(chat_id= "-1002072987116", text = "В настоящее время П5 БОТ не работает. Как только работа восстановится - мы вас оповестим.")

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer(text="Добро пожаловать, выберете действие ниже.", reply_markup=keyboard)

# @dp.message_handler(commands=["chat"])
# async def my_id(msg: types.Message):
#     my_chat_id = msg.chat.id
#     await msg.reply(my_chat_id)

# Команда получения информации с таблицы о заполнении
@dp.message_handler(text=["Статус заполнения Таблицы статей"])
async def status_states_callback(message: types.Message):
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await Function1.function1()
    from Function1 import all_teg, names_state
    if all_teg:
        await bot.send_message(message.from_user.id, "<u><b>Следующим авторам необходимо заполнить Таблицу статей:</b></u>" + "\n" + '\n'.join(all_teg), parse_mode='HTML')
    await bot.send_message(message.from_user.id, "<u><b>Авторам данных статей необходимо заполнить Таблицу статей:</b></u>" + "\n - " + '\n - '.join(names_state), parse_mode='HTML')
    os.remove('Table_Таблица статей.xlsx')
# Команда создания дорожной карты
@dp.message_handler(text=["Дорожная карта написания статей"])
async def notes_states_callback(message: types.Message):
    chat_id = message.from_user.id
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
@dp.message_handler(text=["Ссылка на Таблицу статей"])
async def notes_states_callback(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "<u><b>Ссылка на заполнение Таблицы статей:</b></u>" + "\n" + "https://disk.yandex.ru/i/MYnqCNHmuaALqA",
                         parse_mode='HTML')

# Команда получения информации с таблицы о просроченных статьях
@dp.message_handler(text=["Просроченные статьи"])
async def status_states_callback(message: types.Message):
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await Old_state.function_old_state()
    from Old_state import check_state_in_dict
    await bot.send_message(message.from_user.id, "<u><b>Список просроченных статей:</b></u>" + "\n - " + '\n - '.join(check_state_in_dict), parse_mode='HTML')
    os.remove('Table_Таблица статей.xlsx')

# Команда для заполнения ТГ-формы
# класс для ТГ-формы
class ArticleForm(StatesGroup):
    title = State()
    date = State()
    thesis = State()
    keywords = State()
    authors = State()

@dp.message_handler(text=["Добавить плановую статью"])
async def add_article_callback(message: types.Message):
    keyboard_line_add = InlineKeyboardMarkup(row_width=1)
    keyboard_line_add.add(InlineKeyboardButton("Добавить статью в таблицу", callback_data="add_article"))
    await bot.send_message(message.from_user.id,"Нажмите кнопку, чтобы продолжить", reply_markup=keyboard_line_add)

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
    await bot.send_message(message.from_user.id,"Введите плановую дату публикации (ДД.ММ.ГГГГ):")

@dp.message_handler(state=ArticleForm.date)
async def process_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["date"] = datetime.strptime(message.text, "%d.%m.%Y")
    await ArticleForm.next()
    await bot.send_message(message.from_user.id,"Введите тезис статьи:")

@dp.message_handler(state=ArticleForm.thesis)
async def process_thesis(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["thesis"] = message.text
    await ArticleForm.next()
    await bot.send_message(message.from_user.id,"Введите ключевые слова:")

@dp.message_handler(state=ArticleForm.keywords)
async def process_keywords(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["keywords"] = message.text
    await ArticleForm.next()
    await bot.send_message(message.from_user.id,"Введите имена авторов:")

@dp.message_handler(state=ArticleForm.authors)
async def process_authors(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["authors"] = message.text
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await TG_form_save.function_TG_form_save(os.getenv('SAVE_PATH'), os.getenv('SAVE_PATH'), data["title"], data["date"], data["thesis"], data["authors"], data["keywords"])
    await message.answer("Происходит запись данных")
    await Upload_YD.upload_file_to_yandex_disk(os.getenv('TOKEN'), os.getenv('SAVE_PATH'), os.getenv('DIRECTORY'))
    from Upload_YD import UpLOAD
    if UpLOAD:
        await message.answer("Данные успешно записаны на ЯД")
    else:
        await message.answer("Ошибка записи данных на ЯД. Попробуйте повторить попытку позже.")
    os.remove('Table_Таблица статей.xlsx')
    await state.finish()

# Команда для выполнения подбора статей для цитирования
class ArticlecitatForm(StatesGroup):
    name = State()
@dp.message_handler(text = "Подбор статей для цитирования")
async def add_citat_pre_callback(message: types.Message):
    keyboard_line_cit = InlineKeyboardMarkup(row_width=1)
    keyboard_line_cit.add(InlineKeyboardButton("Подобрать статьи для цитирования", callback_data="state_states"))
    await bot.send_message(message.from_user.id,"Нажмите кнопку, чтобы продолжить", reply_markup=keyboard_line_cit)
@dp.callback_query_handler(lambda c: c.data == "state_states")
async def add_citat_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await ArticlecitatForm.name.set()
    await bot.send_message(callback_query.from_user.id, "Введите название статьи:")

# Обработка заполнения всех полей формы:
@dp.message_handler(state=ArticlecitatForm.name)
async def process_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await Yandex_disk.download_file_from_yandex_disk(os.getenv('TOKEN'), os.getenv('DIRECTORY'), os.getenv('SAVE_PATH'))
    await Macros_citate.bibliography_macros_1(os.getenv('SAVE_PATH'), data['name'])
    from Macros_citate import er_mes_search, er_mes_opub
    user_id = message.from_user.id
    if er_mes_search:
        await bot.send_message(user_id,"Данная статья не найдена. Проверьте соответствие написанного Вами названия с тем названием, которое указано в Таблице статей.")
    elif er_mes_opub:
        await bot.send_message(user_id,"Данная статья уже опубликована. Подбор статей для цитирования не имеет смысла.")
    else:
        from Macros_citate import word_list
        if word_list:
            await message.answer("<u><b>Список возможных статей для цитирования:</b></u>" + "\n - " + '\n - '.join(word_list),
                                parse_mode='HTML')
        else:
            from Macros_citate import withouht_key
            if withouht_key:
                await bot.send_message(user_id,"Список ключевых слов у заданной статьи отсутствует")
            else:
                await bot.send_message(user_id,"Для данной статьи список источников для цитирования не найден.")
    os.remove('Table_Таблица статей.xlsx')
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)