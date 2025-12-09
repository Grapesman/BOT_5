import os

from dotenv import load_dotenv


load_dotenv()


YA_TOKEN = os.getenv('YA_TOKEN')
YA_FILE_PATH = os.getenv('YA_FILE_PATH')

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_NOTIFICATION_ID = os.getenv('TG_NOTIFICATION_ID')
TG_P5_ID = os.getenv('TG_P5_ID')

FILE_SAVE_PATH = os.getenv('FILE_SAVE_PATH')
