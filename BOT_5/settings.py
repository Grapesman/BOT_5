import os

from dotenv import load_dotenv


load_dotenv()



TOKEN = os.getenv('TOKEN')
DIRECTORY = os.getenv('DIRECTORY')
TOKEN_bot = os.getenv('TOKEN_bot')
SAVE_PATH = os.getenv('SAVE_PATH')
TG_NOTIFICATION_ID = os.getenv('TG_NOTIFICATION_ID')