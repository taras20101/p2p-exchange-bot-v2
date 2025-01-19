from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 Купити USDT", "💱 Продати USDT"],
        ["📊 Перегляд спредів", "⚙️ Налаштування"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👋 Вітаю! Я бот для обміну USDT.\n\n"
        "Оберіть дію:",
        reply_markup=reply_markup
    ) 