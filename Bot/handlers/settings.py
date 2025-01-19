from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
import json

# Стани розмови
SETTINGS_MENU = range(1)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отримуємо поточні налаштування
    verified_only = context.user_data.get('verified_only', False)
    limit_amount = context.user_data.get('limit_amount', 0)
    transaction_amount = context.user_data.get('transaction_amount', 0)
    selected_exchange = context.user_data.get('exchange', 'binance')
    
    keyboard = [
        [InlineKeyboardButton(
            f"🏦 Біржа: {selected_exchange.capitalize()}", 
            callback_data='toggle_exchange'
        )],
        [InlineKeyboardButton(
            f"✅ Тільки верифіковані: {'Увімк' if verified_only else 'Вимк'}", 
            callback_data='toggle_verified'
        )],
        [InlineKeyboardButton(
            f"💎 Ліміт ордера (USDT): {limit_amount if limit_amount > 0 else 'Не встановлено'}", 
            callback_data='set_limit'
        )],
        [InlineKeyboardButton(
            f"💵 Сума транзакції (UAH): {transaction_amount if transaction_amount > 0 else 'Не встановлено'}", 
            callback_data='set_transaction'
        )],
        [InlineKeyboardButton("🔄 Скинути налаштування", callback_data='reset_settings')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(
                "⚙️ Налаштування\n\n"
                "Оберіть параметр для зміни:",
                reply_markup=reply_markup
            )
        except Exception as e:
            # Якщо повідомлення не змінилося, просто ігноруємо помилку
            pass
    else:
        await update.message.reply_text(
            "⚙️ Налаштування\n\n"
            "Оберіть параметр для зміни:",
            reply_markup=reply_markup
        )
    return SETTINGS_MENU

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'toggle_exchange':
        current = context.user_data.get('exchange', 'binance')
        context.user_data['exchange'] = 'bybit' if current == 'binance' else 'binance'
        await settings_command(update, context)
    
    elif query.data == 'save_h1':
        # Зберігаємо поточні налаштування як H1
        settings = {
            'verified_only': context.user_data.get('verified_only', False),
            'limit_amount': context.user_data.get('limit_amount', 0),
            'transaction_amount': context.user_data.get('transaction_amount', 0),
            'exchange': context.user_data.get('exchange', 'binance')
        }
        context.user_data['h1_settings'] = settings
        await query.message.reply_text("✅ Налаштування H1 збережено")
        await settings_command(update, context)
    
    elif query.data == 'load_h1':
        # Завантажуємо налаштування H1
        if 'h1_settings' in context.user_data:
            settings = context.user_data['h1_settings']
            context.user_data.update(settings)
            await query.message.reply_text("✅ Налаштування H1 завантажено")
        else:
            await query.message.reply_text("❌ Налаштування H1 не знайдено")
        await settings_command(update, context)
    
    elif query.data == 'toggle_verified':
        context.user_data['verified_only'] = not context.user_data.get('verified_only', False)
        await settings_command(update, context)
        return SETTINGS_MENU
    
    elif query.data == 'set_limit':
        keyboard = [["🔙 Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text(
            "💎 Введіть мінімальний ліміт ордера в USDT (0 для відключення):\n\n"
            "Будуть показані тільки оголошення з сумою більше або рівною вказаній",
            reply_markup=reply_markup
        )
        return 'ENTER_LIMIT'
    
    elif query.data == 'set_transaction':
        keyboard = [["🔙 Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text(
            "💵 Введіть суму транзакції в UAH (0 для відключення):\n\n"
            "Будуть показані оголошення, що підтримують вказану суму транзакції",
            reply_markup=reply_markup
        )
        return 'ENTER_TRANSACTION'
    
    elif query.data == 'reset_settings':
        context.user_data.clear()
        context.user_data['verified_only'] = False
        context.user_data['limit_amount'] = 0
        context.user_data['transaction_amount'] = 0
        await query.message.reply_text("✅ Налаштування скинуто до початкових значень")
        await settings_command(update, context)

async def enter_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Назад":
        await settings_command(update, context)
        return SETTINGS_MENU
        
    try:
        amount = float(update.message.text)
        if amount < 0:
            raise ValueError
        context.user_data['limit_amount'] = amount
        await settings_command(update, context)
        return SETTINGS_MENU
    except ValueError:
        await update.message.reply_text("❌ Будь ласка, введіть коректне додатне число")
        return 'ENTER_LIMIT'

async def enter_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Назад":
        await settings_command(update, context)
        return SETTINGS_MENU
        
    try:
        amount = float(update.message.text)
        if amount < 0:
            raise ValueError
        context.user_data['transaction_amount'] = amount
        await settings_command(update, context)
        return SETTINGS_MENU
    except ValueError:
        await update.message.reply_text("❌ Будь ласка, введіть коректне додатне число")
        return 'ENTER_TRANSACTION' 