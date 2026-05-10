import logging
import os
import traceback

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.handlers.start import start, help_command
from bot.handlers.router import route_text, route_photo
from bot.handlers.broadcast_handler import broadcast_command
from bot.handlers.verification_handler import handle_verification_callback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)
logging.getLogger("bot").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling update:\n%s", traceback.format_exc())


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set.")

    app = Application.builder().token(token).build()

    app.add_error_handler(error_handler)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CallbackQueryHandler(handle_verification_callback, pattern="^verify_"))

    app.add_handler(
        MessageHandler(filters.PHOTO | filters.Document.IMAGE, route_photo)
    )

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, route_text)
    )

    logger.info("Bot is starting...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
