from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services import (
    binance_api, mexc_api, bybit_api, 
    bingx_api, okx_api, kucoin_api, bitget_api
)

async def show_arbitrage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отримуємо пропозиції з усіх бірж
    exchanges = {
        'Binance': binance_api.BinanceAPI,
        'MEXC': mexc_api.MexcAPI,
        'Bybit': bybit_api.BybitAPI,
        'BingX': bingx_api.BingXAPI,
        'OKX': okx_api.OkxAPI,
        'KuCoin': kucoin_api.KuCoinAPI,
        'Bitget': bitget_api.BitgetAPI
    }
    
    # Збираємо найкращі пропозиції для купівлі і продажу
    buy_offers = []
    sell_offers = []
    
    for name, api in exchanges.items():
        buy_offers.extend(api.get_buy_offers(context))
        sell_offers.extend(api.get_sell_offers(context))
    
    # Знаходимо найкращі варіанти
    best_buy = min(buy_offers, key=lambda x: x['price'])
    best_sell = max(sell_offers, key=lambda x: x['price'])
    
    # Рахуємо спред
    spread = best_sell['price'] - best_buy['price']
    spread_percent = (spread / best_buy['price']) * 100
    
    message = (
        "📈 Найкращі можливості для арбітражу:\n\n"
        f"💰 Купівля: {best_buy['exchange']}\n"
        f"Ціна: {best_buy['price']:.2f} UAH\n"
        f"Продавець: {best_buy['merchant']}\n"
        f"Доступно: {best_buy['amount']:.2f} USDT\n\n"
        f"💱 Продаж: {best_sell['exchange']}\n"
        f"Ціна: {best_sell['price']:.2f} UAH\n"
        f"Покупець: {best_sell['merchant']}\n"
        f"Доступно: {best_sell['amount']:.2f} USDT\n\n"
        f"📊 Потенційний прибуток:\n"
        f"Спред: {spread:.2f} UAH\n"
        f"Відсоток: {spread_percent:.2f}%"
    )
    
    await update.message.reply_text(message) 