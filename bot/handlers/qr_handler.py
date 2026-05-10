import io
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.utils.qr_generator import generate_qr
from bot.keyboards import MAIN_KEYBOARD, CANCEL_KEYBOARD, INSTAGRAM_BUTTON
from bot import states


async def start_qr_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = states.AWAIT_QR_TEXT
    await update.message.reply_text(
        "What should the QR code say? Send me a URL or any text.",
        reply_markup=CANCEL_KEYBOARD,
    )


async def do_qr(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    if len(text) > 500:
        await update.message.reply_text("That's too long (max 500 characters). Try something shorter.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

    try:
        qr_bytes = generate_qr(text)
        context.user_data["state"] = states.IDLE

        await update.message.reply_photo(
            photo=io.BytesIO(qr_bytes),
            caption=(
                f"QR code ready.\n"
                f"Faster than your internet speed. 😼\n\n"
                f"Encoded: {text}"
            ),
            reply_markup=MAIN_KEYBOARD,
        )
        await update.message.reply_text(
            "Anything else?",
            reply_markup=INSTAGRAM_BUTTON,
        )
    except Exception as e:
        await update.message.reply_text(f"Failed to generate QR code: {e}", reply_markup=MAIN_KEYBOARD)
        context.user_data["state"] = states.IDLE
