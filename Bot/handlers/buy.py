from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from services.binance_api import BinanceAPI
from services.bybit_api import BybitAPI

# Стани розмови
CHOOSE_EXCHANGE = range(1)

async def buy_usdt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Binance P2P", callback_data='buy_binance')],
        [InlineKeyboardButton("OKX P2P", callback_data='buy_okx')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏦 Оберіть біржу для купівлі USDT:",
        reply_markup=reply_markup
    )
    return CHOOSE_EXCHANGE

async def exchange_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back':
        keyboard = [
            ["💰 Купити USDT", "💱 Продати USDT"],
            ["📊 Перегляд спредів", "⚙️ Налаштування"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text("Оберіть дію:", reply_markup=reply_markup)
        return ConversationHandler.END
    
    # Отримуємо налаштування
    verified_only = context.user_data.get('verified_only', False)
    limit_amount = context.user_data.get('limit_amount', 0)
    transaction_amount = context.user_data.get('transaction_amount', 0)
    
    # Вибираємо API в залежності від біржі
    if query.data == 'buy_binance':
        offers = BinanceAPI.get_buy_offers(context=context)
        exchange = "Binance"
    else:
        offers = BybitAPI.get_p2p_offers(side='BUY', verified_only=verified_only, 
                                       limit_amount=limit_amount, 
                                       transaction_amount=transaction_amount)
        exchange = "Bybit"
    
    if not offers:
        keyboard = [
            ["💰 Купити USDT", "💱 Продати USDT"],
            ["📊 Перегляд спредів", "⚙️ Налаштування"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text(
            "❌ Не знайдено пропозицій.\n"
            "Спробуйте пізніше або змініть налаштування.",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    
    message = f"💰 Найкращі пропозиції для купівлі USDT на {exchange}:\n\n"
    
    for i, offer in enumerate(offers, 1):
        message += (
            f"{i}. Ціна: {offer['price']:.2f} UAH\n"
            f"👤 Продавець: {offer['merchant']} | ⭐ {offer['completion']}\n"
            f"💎 Доступно: {offer['amount']} USDT\n"
            f"🏦 Оплата: {', '.join(offer['payment_methods'])}\n\n"
        )
    
    keyboard = [
        ["💰 Купити USDT", "💱 Продати USDT"],
        ["📊 Перегляд спредів", "⚙️ Налаштування"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await query.message.reply_text(message, reply_markup=reply_markup)
    return ConversationHandler.END

async def amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Назад":
        keyboard = [
            ["Купити USDT", "Продати USDT"],
            ["Перегляд спредів", "Налаштування"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Головне меню:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
        
    try:
        amount_uah = float(update.message.text)
        price = BinanceAPI.get_usdt_price()
        
        if price is None:
            await update.message.reply_text("Помилка отримання курсу. Спробуйте пізніше.")
            return ConversationHandler.END
        
        usdt_amount = amount_uah / price
        
        keyboard = [
            ["Купити USDT", "Продати USDT"],
            ["Перегляд спредів", "Налаштування"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"💰 Купівля USDT\n\n"
            f"Сума в UAH: {amount_uah:.2f}\n"
            f"Курс: {price:.2f} UAH\n"
            f"Ви отримаєте: {usdt_amount:.2f} USDT\n\n"
            f"Для оплати доступні:\n"
            f"- Monobank\n"
            f"- PrivatBank\n"
            f"- інші карти",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть коректну суму.")
        return CHOOSE_EXCHANGE 