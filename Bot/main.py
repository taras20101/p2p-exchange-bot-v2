# -*- coding: utf-8 -*-
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

from config import TOKEN
from handlers import start, buy, sell, spreads, settings

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Помилка: {context.error}")
    if update.message:
        await update.message.reply_text("Сталася помилка. Спробуйте ще раз.")
    elif update.callback_query:
        await update.callback_query.message.reply_text("Сталася помилка. Спробуйте ще раз.")

async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Отримано повідомлення: {update.message.text}")

def main():
    logger.info("Запуск бота...")
    
    # Створення застосунку
    application = Application.builder().token(TOKEN).build()

    # Додавання обробника команди start
    application.add_handler(CommandHandler("start", start.start_command))
    logger.info("Додано обробник команди start")
    
    # Додавання обробників для купівлі/продажу
    buy_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💰 Купити USDT$"), buy.buy_usdt)],
        states={
            buy.CHOOSE_EXCHANGE: [CallbackQueryHandler(buy.exchange_callback)]
        },
        fallbacks=[MessageHandler(filters.Regex("^🔙 Назад$"), start.start_command)]
    )
    application.add_handler(buy_handler)

    sell_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💱 Продати USDT$"), sell.sell_usdt)],
        states={
            sell.CHOOSE_EXCHANGE: [CallbackQueryHandler(sell.exchange_callback)]
        },
        fallbacks=[MessageHandler(filters.Regex("^🔙 Назад$"), start.start_command)]
    )
    application.add_handler(sell_handler)

    # Додавання обробника для налаштувань
    settings_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^⚙️ Налаштування$"), settings.settings_command),
            CommandHandler("settings", settings.settings_command)
        ],
        states={
            settings.SETTINGS_MENU: [
                CallbackQueryHandler(settings.button_callback),
                MessageHandler(filters.Regex("^⚙️ Налаштування$"), settings.settings_command)
            ],
            'ENTER_LIMIT': [MessageHandler(filters.TEXT & ~filters.COMMAND, settings.enter_limit)],
            'ENTER_TRANSACTION': [MessageHandler(filters.TEXT & ~filters.COMMAND, settings.enter_transaction)]
        },
        fallbacks=[MessageHandler(filters.Regex("^🔙 Назад$"), start.start_command)],
        per_message=False
    )
    application.add_handler(settings_handler)
    logger.info("Додано обробник налаштувань")
    
    # Додавання обробника для перегляду спредів
    application.add_handler(MessageHandler(filters.Regex("^📊 Перегляд спредів$"), spreads.show_spreads))
    logger.info("Додано обробник перегляду спредів")

    # Додавання обробника для відлагодження
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, debug_handler))

    # Додавання обробника помилок
    application.add_error_handler(error_handler)
    logger.info("Додано обробник помилок")

    # Запуск бота
    logger.info("Запуск polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 