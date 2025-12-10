import settings
from loader import bot
from logger import logger


async def notify(chat_id: int, message: str):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление для ID: {chat_id}\nДетали: {e}")


async def notify_admins(message: str):
    admin_message = "[ADMIN] " + message
    for notification_id in settings.TG_NOTIFICATION_IDS:
        await notify(notification_id, admin_message)
