from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ApplicationHandlerStop

from handlers import start,handle_text
from settings import BOT_TOKEN
import logging
from  database_operations import initiate_connection

from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def global_exception_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle unexpected exceptions globally, including timeouts.
    """
    logger.error(f"Unhandled exception: {context.error}")

    if isinstance(context.error, (telegram.error.TimedOut, httpx.Timeout)):
        logger.error("Timeout detected. Restarting interaction.")
        # Restart interaction using the `start` function
        if isinstance(update, Update):
            await start(update, context)

    # Optionally stop further processing
    raise ApplicationHandlerStop()



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    logger.info("Starting bot application...")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_error_handler(global_exception_handler)


    # Add handlers
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
