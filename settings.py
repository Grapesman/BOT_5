import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


YA_TOKEN = os.getenv('YA_TOKEN')
YA_FILE_PATH = os.getenv('YA_FILE_PATH')
YA_TABLE_URL = os.getenv('YA_TABLE_URL')
YA_REQUEST_PROXY = os.getenv('YA_REQUEST_PROXY') or None
YA_REFRESH_INTERVAL_MINUTES = int(os.getenv('YA_REFRESH_INTERVAL_MINUTES') or 3)

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_P5_ID = os.getenv('TG_P5_ID')
TG_NOTIFICATION_IDS = [i.strip() for i in os.getenv('TG_NOTIFICATION_IDS').split(",")]

BASE_DIR = Path(__file__).resolve().parent
# Таблица для команд чтения, обновляется по расписанию
READ_TABLE_PATH = BASE_DIR / 'table-for-read.xlsx'
# Таблица для добавления статьи, удаляется после загрузки на Яндекс-диск
WRITE_TABLE_PATH = BASE_DIR / 'table-for-write.xlsx'
