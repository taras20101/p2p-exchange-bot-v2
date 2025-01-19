import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot токен
TOKEN = os.getenv('BOT_TOKEN')

# Налаштування Binance API
BINANCE_API_URL = "https://api.binance.com"
USDT_UAH_SYMBOL = "USDTUAH"

# Інтервал оновлення курсів (у секундах)
UPDATE_INTERVAL = 300  # 5 хвилин 