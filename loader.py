from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import settings


bot = Bot(token=settings.TG_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
