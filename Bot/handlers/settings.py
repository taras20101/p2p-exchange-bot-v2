from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
import json

# Стани розмови
SETTINGS_MENU = range(1)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Перевіряємо, чи це callback_query чи звичайне повідомлення
    if update.callback_query:
        message = update.callback_query.message
        await update.callback_query.answer()
    else:
        message = update.message

    keyboard = [
        [InlineKeyboardButton("Змінити мінімальну суму", callback_data='min_amount')],
        [InlineKeyboardButton("Змінити максимальну суму", callback_data='max_amount')],
        [InlineKeyboardButton("Змінити платіжні методи", callback_data='payment_methods')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "⚙️ Налаштування:\n\n" \
           "Мінімальна сума: 1000 UAH\n" \
           "Максимальна сума: 200000 UAH\n" \
           "Платіжні методи: Монобанк, Приват24"

    if update.callback_query:
        await message.edit_text(text, reply_markup=reply_markup)
    else:
        await message.reply_text(text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back':
        from .start import start_command
        await start_command(update, context)
        return
        
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