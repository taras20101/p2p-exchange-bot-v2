from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services.binance_api import BinanceAPI

async def show_spreads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 Купити USDT", "💱 Продати USDT"],
        ["📊 Перегляд спредів", "⚙️ Налаштування"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Отримуємо налаштування
    verified_only = context.user_data.get('verified_only', False)
    limit_amount = context.user_data.get('limit_amount', 0)
    transaction_amount = context.user_data.get('transaction_amount', 0)
    
    # Отримуємо актуальні пропозиції з урахуванням фільтрів
    buy_offers = BinanceAPI.get_buy_offers(context=context)
    sell_offers = BinanceAPI.get_sell_offers(context=context)
    
    if not buy_offers or not sell_offers:
        await update.message.reply_text(
            "❌ Не вдалося отримати дані для розрахунку спреду.\n"
            "Спробуйте пізніше або змініть налаштування.",
            reply_markup=reply_markup
        )
        return
    
    # Знаходимо найкращі ціни
    best_buy = min(buy_offers, key=lambda x: x['price'])
    best_sell = max(sell_offers, key=lambda x: x['price'])
    
    # Інвертуємо спред: якщо від'ємний - робимо додатним, якщо додатний - від'ємним
    spread = best_buy['price'] - best_sell['price']  # Змінили порядок віднімання
    spread_percent = (spread / best_sell['price']) * 100
    
    # Додаємо знак + для додатних значень
    spread_str = f"+{spread:.2f}" if spread > 0 else f"{spread:.2f}"
    spread_percent_str = f"+{spread_percent:.2f}" if spread_percent > 0 else f"{spread_percent:.2f}"
    
    message = (
        "📊 Аналіз спредів P2P\n\n"
        f"💰 Найкраща ціна купівлі: {best_buy['price']:.2f} UAH\n"
        f"💎 Доступно: {best_buy['amount']:.2f} USDT\n"
        f"👤 Продавець: {best_buy['merchant']} | ⭐ {best_buy['completion']}\n\n"
        f"💱 Найкраща ціна продажу: {best_sell['price']:.2f} UAH\n"
        f"💎 Доступно: {best_sell['amount']:.2f} USDT\n"
        f"👤 Покупець: {best_sell['merchant']} | ⭐ {best_sell['completion']}\n\n"
        f"📈 Спред: {spread_str} UAH ({spread_percent_str}%)"
    )
    
    # Додаємо інформацію про активні фільтри
    if verified_only or limit_amount > 0 or transaction_amount > 0:
        message += "\n\n🔍 Активні фільтри:\n"
        if verified_only:
            message += "✅ Тільки верифіковані мерчанти\n"
        if limit_amount > 0:
            message += f"💎 Мінімальна сума: {limit_amount} USDT\n"
        if transaction_amount > 0:
            message += f"💵 Сума транзакції: {transaction_amount} UAH\n"
    
    await update.message.reply_text(message, reply_markup=reply_markup) 