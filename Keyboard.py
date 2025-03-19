from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
b1 = KeyboardButton("Добавить плановую статью")
b2 = KeyboardButton("Статус заполнения Таблицы статей")
b3 = KeyboardButton("Дорожная карта написания статей")
b4 = KeyboardButton("Ссылка на Таблицу статей")
b5 = KeyboardButton("Просроченные статьи")
b6 = KeyboardButton("Подбор статей для цитирования")
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

# Добавляем кнопки в клавиатуру
keyboard.add(b1).insert(b2).add(b3).insert(b4).add(b5).insert(b6)