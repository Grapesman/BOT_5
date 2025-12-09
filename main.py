import logging
from datetime import datetime
from Keyboard import keyboard

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import settings
import Function1, Function2, Graph, Old_state, Macros_citate, statistic, hirsh
from data_manager import DataManager


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание объектов бота и диспетчера
bot = Bot(token=settings.TG_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

async def setup_scheduler():
    """Настройка и запуск планировщика"""
    scheduler.add_job(send_weekly_message, 'cron', day_of_week='mon', hour=10, minute=00)
    scheduler.add_job(send_daily_message, 'cron', day_of_week='mon', hour=11, minute=00)
    scheduler.add_job(
        send_analize_message,
        'cron',
        month='1,4,7,10',  # январь, апрель, июль, октябрь
        day=1,
        hour=10,
        minute=30
    )

    scheduler.add_job(
        send_hirsh_remember_message,
        'cron',
        month='1,4,7,10',  # январь, апрель, июль, октябрь
        day=1,
        hour=10,
        minute=20
    )
    scheduler.start()


async def on_startup(dp):
    # await bot.send_message(chat_id=settings.TG_NOTIFICATION_ID, text="БОТ П5 активен.")
    # await bot.send_message(chat_id=settings.TG_NOTIFICATION_ID, text="Добро пожаловать, выберете действие ниже.",
    #                        reply_markup=keyboard)
    # Запуск планировщика в отдельной задаче
    asyncio.create_task(setup_scheduler())


# async def on_shutdown(dp):
#     await bot.send_message(chat_id=settings.TG_NOTIFICATION_ID,
#                            text="В настоящее время П5 БОТ не работает.")


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer(text="Добро пожаловать, выберете действие ниже.", reply_markup=keyboard)


# Команда получения информации с таблицы о заполнении
@dp.message_handler(text=["Статус заполнения Таблицы статей"])
async def status_states_callback(message: types.Message):
    await Function1.function1()
    from Function1 import all_teg, names_state
    if all_teg:
        await bot.send_message(message.from_user.id,
                               "<u><b>Следующим авторам необходимо заполнить Таблицу статей:</b></u>" + "\n" + '\n'.join(
                                   all_teg), parse_mode='HTML')
    await bot.send_message(message.from_user.id,
                           "<u><b>Авторам данных статей необходимо заполнить Таблицу статей:</b></u>" + "\n - " + '\n - '.join(
                               names_state), parse_mode='HTML')


# Команда создания дорожной карты
@dp.message_handler(text=["Дорожная карта написания статей"])
async def notes_states_callback(message: types.Message):
    chat_id = message.from_user.id
    await Function2.function2()
    from Function2 import check_state_in_dict, date_check_make_in_dict, date_state_3m
    await Graph.graf(check_state_in_dict, date_check_make_in_dict, date_state_3m)
    from Graph import buf
    try:
        await bot.send_photo(chat_id=chat_id, photo=buf,
                             caption="<b>Дорожная карта статей.</b> Представлены статьи, планируемые к публикации в ближайшие 6 месяцев.",
                             parse_mode='HTML')
        buf.close()
    except Exception as e:
        print(f"Ошибка при отправке фотографии: {e}")


# Команда отправки ссылки на таблицу с Яндекс-диска
@dp.message_handler(text=["Ссылка на Таблицу статей"])
async def notes_states_callback(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "<u><b>Ссылка на заполнение Таблицы статей:</b></u>" + "\n" + "https://disk.yandex.ru/i/MYnqCNHmuaALqA",
                           parse_mode='HTML')


# Команда получения информации Анализа сообщества
@dp.message_handler(text=["Анализ деятельности сообщества"])
async def status_states_callback(message: types.Message):
    await statistic.function_statistic()
    from statistic import checking, last_checking
    from statistic import cit_now, cit_last
    await bot.send_message(message.from_user.id,
                           "<u><b>Анализ деятельности сообщества за текущие 3 месяца.</b></u>" + "\n" + "Количество опубликованных статей: " + str(checking) + " (за прошлый период: " + str(last_checking) +")"  + "\n" + "Количество цитирований: " + str(cit_now) + " (за прошлый период: " + str(cit_last) +")",
                           parse_mode='HTML')
    from statistic import how_much_ratingQ1, how_much_ratingQ2, how_much_ratingQ3, how_much_ratingQ4, how_much_ratingCP, \
        how_much_ratingVAK, how_much_ratingRINC
    if how_much_ratingQ1:
        await bot.send_message(message.from_user.id,
                               "За текущий квартал количество опубликованных статей рейтинга Q1 составляет: " + str(
                                   how_much_ratingQ1),
                               parse_mode='HTML')
    if how_much_ratingQ2:
        await bot.send_message(message.from_user.id,
                               "За текущий квартал количество опубликованных статей рейтинга Q2 составляет: " + str(
                                   how_much_ratingQ2),
                               parse_mode='HTML')
    if how_much_ratingQ3:
        await bot.send_message(message.from_user.id,
                               "За текущий квартал количество опубликованных статей рейтинга Q3 составляет: " + str(
                                   how_much_ratingQ3),
                               parse_mode='HTML')
    if how_much_ratingQ4:
        await bot.send_message(message.from_user.id,
                               "За текущий квартал количество опубликованных статей рейтинга Q4 составляет: " + str(
                                   how_much_ratingQ4),
                               parse_mode='HTML')
    if how_much_ratingCP:
        await bot.send_message(message.from_user.id,
                               "За текущий квартал количество опубликованных статей рейтинга Conference Paper составляет: " + str(
                                   how_much_ratingCP),
                               parse_mode='HTML')
    if how_much_ratingVAK:
        await bot.send_message(message.from_user.id,
                               "За текущий квартал количество опубликованных статей рейтинга ВАК составляет: " + str(
                                   how_much_ratingVAK),
                               parse_mode='HTML')
    if how_much_ratingRINC:
        await bot.send_message(message.from_user.id,
                               "За текущий квартал количество опубликованных статей рейтинга РИНЦ составляет: " + str(
                                   how_much_ratingRINC),
                               parse_mode='HTML')
    await hirsh.hirsh_function()
    from hirsh import data_dict
    if data_dict:
        await bot.send_message(message.from_user.id,
                                   "В настоящее время, у " +  str(data_dict) + " членов НСП5 индекс Хирша превышает единицу." , parse_mode='HTML')
# Команда получения информации с таблицы о просроченных статьях
@dp.message_handler(text=["Просроченные статьи"])
async def status_states_callback(message: types.Message):
    await Old_state.function_old_state()
    from Old_state import check_state_in_dict
    await bot.send_message(message.from_user.id,
                           "<u><b>Список просроченных статей:</b></u>" + "\n - " + '\n - '.join(check_state_in_dict),
                           parse_mode='HTML')

# Функция для автоматического формирования сообщения об анализе деятельности сообщества
async def send_analize_message():
    await statistic.function_statistic()
    from statistic import checking, last_checking
    from statistic import cit_now, cit_last

    await bot.send_message(settings.TG_NOTIFICATION_ID,
                           "<u><b>Анализ деятельности сообщества за текущие 3 месяца.</b></u>" + "\n" + "Количество опубликованных статей: " + str(checking) + " (за прошлый период: " + str(last_checking) +")"  + "\n" + "Количество цитирований: " + str(cit_now) + " (за прошлый период: " + str(cit_last) +")",
                           parse_mode='HTML')
    from statistic import how_much_ratingQ1, how_much_ratingQ2, how_much_ratingQ3, how_much_ratingQ4, how_much_ratingCP, \
        how_much_ratingVAK, how_much_ratingRINC
    if how_much_ratingQ1:
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                               "За текущий квартал количество опубликованных статей рейтинга Q1 составляет: "+str(how_much_ratingQ1),
                               parse_mode='HTML')
    if how_much_ratingQ2:
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                               "За текущий квартал количество опубликованных статей рейтинга Q2 составляет: "+str(how_much_ratingQ2),
                               parse_mode='HTML')
    if how_much_ratingQ3:
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                               "За текущий квартал количество опубликованных статей рейтинга Q3 составляет: "+str(how_much_ratingQ3),
                               parse_mode='HTML')
    if how_much_ratingQ4:
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                               "За текущий квартал количество опубликованных статей рейтинга Q4 составляет: "+str(how_much_ratingQ4),
                               parse_mode='HTML')
    if how_much_ratingCP:
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                               "За текущий квартал количество опубликованных статей рейтинга Conference Paper составляет: "+str(how_much_ratingCP),
                               parse_mode='HTML')
    if how_much_ratingVAK:
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                               "За текущий квартал количество опубликованных статей рейтинга ВАК составляет: "+str(how_much_ratingVAK),
                               parse_mode='HTML')
    if how_much_ratingRINC:
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                               "За текущий квартал количество опубликованных статей рейтинга РИНЦ составляет: "+str(how_much_ratingRINC),
                               parse_mode='HTML')
    await hirsh.hirsh_function()
    from hirsh import data_dict
    if data_dict:
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                                   "В настоящее время, у " +  str(data_dict) + " членов НСП5 индекс Хирша превышает единицу." , parse_mode='HTML')
# Отправка сообщения о напоминании заполнения своего индекса ХИРШа 1 раз в квартал
async def send_hirsh_remember_message():
    await bot.send_message(settings.TG_NOTIFICATION_ID,
                           "Уважаемые коллеги, прошу вас обновить значение вашего индекса Хирша в таблице статей, на листе Community.")
# Ежедневное сообщение в чат о просроченных статьях и статусе заполнения таблицы статей
async def send_daily_message():
    try:
        await Old_state.function_old_state()
        from Old_state import check_state_in_dict
        await bot.send_message(settings.TG_NOTIFICATION_ID, "<u><b>Список просроченных статей:</b></u>" + "\n - " + '\n - '.join(
                               check_state_in_dict), parse_mode='HTML')
        await Function1.function1()
        from Function1 import all_teg, names_state
        if all_teg:
            await bot.send_message(settings.TG_NOTIFICATION_ID,
                                   "<u><b>Следующим авторам необходимо заполнить Таблицу статей:</b></u>" + "\n" + '\n'.join(
                                       all_teg), parse_mode='HTML')
        await bot.send_message(settings.TG_NOTIFICATION_ID,
                               "<u><b>Авторам данных статей необходимо заполнить Таблицу статей:</b></u>" + "\n - " + '\n - '.join(
                                   names_state), parse_mode='HTML')
        logging.info("Сообщение отправлено успешно.")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")



#Еженедельное сообщение в чат ДК
async def send_weekly_message():
    try:
        await Function2.function2()
        from Function2 import check_state_in_dict, date_check_make_in_dict, date_state_3m
        await Graph.graf(check_state_in_dict, date_check_make_in_dict, date_state_3m)
        from Graph import buf
        try:
            await bot.send_photo(-1002370442535, photo=buf,
                                 caption="<b>Дорожная карта статей.</b> Представлены статьи, планируемые к публикации в ближайшие 6 месяцев.",
                                 parse_mode='HTML')
            buf.close()
        except Exception as e:
            print(f"Ошибка при отправке фотографии: {e}")
        logging.info("Сообщение отправлено успешно.")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")
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
    await bot.send_message(message.from_user.id, "Нажмите кнопку, чтобы продолжить", reply_markup=keyboard_line_add)


@dp.callback_query_handler(lambda c: c.data == "add_article")
async def add_article_callback_but(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await ArticleForm.title.set()
    await bot.send_message(callback_query.from_user.id, "Введите название статьи:")


# Обработка заполнения всех полей формы:
@dp.message_handler(state=ArticleForm.title)
async def process_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["title"] = message.text
    await ArticleForm.next()  # Переходим к следующему состоянию
    await bot.send_message(message.from_user.id, "Введите плановую дату публикации (ДД.ММ.ГГГГ):")


@dp.message_handler(state=ArticleForm.date)
async def process_date(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data["date"] = datetime.strptime(message.text, "%d.%m.%Y")
        await ArticleForm.next()
        await bot.send_message(message.from_user.id, "Введите тезис статьи:")
    except ValueError:
        await bot.send_message(message.from_user.id,
                               "Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:")
        async with state.proxy() as data:
            data["date"] = datetime.strptime(message.text, "%d.%m.%Y")
        await ArticleForm.next()
        await bot.send_message(message.from_user.id, "Введите тезис статьи:")


@dp.message_handler(state=ArticleForm.thesis)
async def process_thesis(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["thesis"] = message.text
    await ArticleForm.next()
    await bot.send_message(message.from_user.id, "Введите ключевые слова:")


@dp.message_handler(state=ArticleForm.keywords)
async def process_keywords(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["keywords"] = message.text
    await ArticleForm.next()
    await bot.send_message(message.from_user.id, "Введите имена авторов:")


@dp.message_handler(state=ArticleForm.authors)
async def process_authors(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["authors"] = message.text
    await message.answer("Происходит запись данных")

    uploaded: bool = await DataManager.add_new_article_in_yandex(
        data["title"],
        data["date"],
        data["thesis"],
        data["authors"],
        data["keywords"]
    )
    await state.finish()

    if uploaded:
        await message.answer("Данные успешно записаны на Яндекс Диск")
    else:
        await message.answer("Ошибка записи данных на Яндекс Диск. Попробуйте повторить попытку позже.")


# Команда для выполнения подбора статей для цитирования
class ArticlecitatForm(StatesGroup):
    name = State()


@dp.message_handler(text="Подбор статей для цитирования")
async def add_citat_pre_callback(message: types.Message):
    keyboard_line_cit = InlineKeyboardMarkup(row_width=1)
    keyboard_line_cit.add(InlineKeyboardButton("Подобрать статьи для цитирования", callback_data="state_states"))
    await bot.send_message(message.from_user.id, "Нажмите кнопку, чтобы продолжить", reply_markup=keyboard_line_cit)


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
    await Macros_citate.bibliography_macros_1(data['name'])
    from Macros_citate import er_mes_search, er_mes_opub
    user_id = message.from_user.id
    if er_mes_search:
        await bot.send_message(user_id,
                               "Данная статья не найдена. Проверьте соответствие написанного Вами названия с тем названием, которое указано в Таблице статей.")
    elif er_mes_opub:
        await bot.send_message(user_id,
                               "Данная статья уже опубликована. Подбор статей для цитирования не имеет смысла.")
    else:
        from Macros_citate import word_list
        if word_list:
            await message.answer(
                "<u><b>Список возможных статей для цитирования:</b></u>" + "\n - " + '\n - '.join(word_list),
                parse_mode='HTML')
        else:
            from Macros_citate import withouht_key
            if withouht_key:
                await bot.send_message(user_id, "Список ключевых слов у заданной статьи отсутствует")
            else:
                await bot.send_message(user_id, "Для данной статьи список источников для цитирования не найден.")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)