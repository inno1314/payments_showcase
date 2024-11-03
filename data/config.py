from dotenv import load_dotenv
from os import getenv

from database.db_api import UsersDataBase


load_dotenv()


db = UsersDataBase(r"database/tgbot_users.sqlite3")
admins = []

BOT_TOKEN = str(getenv("BOT_TOKEN"))
YOOMONEY_TOKEN = str(getenv('YOOMONEY_TOKEN'))
YOOMONEY_WALLET = str(getenv('YOOMONEY_WALLET'))
CRYPTO_BOT_TOKEN = str(getenv('CRYPTO_BOT_TOKEN'))
AAIO_API_KEY = str(getenv('AAIO_API_KEY'))
AAIO_MERCHANT_ID = str(getenv('AAIO_MERCHANT_ID'))
AAIO_SECRET_KEY = str(getenv('AAIO_SECRET_KEY'))
