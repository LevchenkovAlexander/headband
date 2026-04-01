import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DB_ADDRESS = os.getenv('DB_ADDRESS')
    MINI_APP_URL = os.getenv('MINI_APP_URL', 'https://your-mini-app.com')

    # Тарифы подписки
    SUBSCRIPTION_PRICES = {
        'month': {'days': 30, 'price': 990}
    }