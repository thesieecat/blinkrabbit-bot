import io
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.utils.image_compress import compress_image
from bot.keyboards import MAIN_KEYBOARD, CANCEL_KEYBOARD, INSTAGRAM_BUTTON
from bot import states


async def start_compress_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = states.AWAIT_COMPRESS
    await update.message.reply_text(
        "Send me the image you want to compress.",
        reply_markup=CANCEL_KEYBOARD,
    )


async def do_compress(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)

    try:
        compressed, original_size, new_size = compress_image(image_bytes)
        reduction = 100 * (1 - new_size / original_size) if original_size else 0
        context.user_data["state"] = states.IDLE

        await update.message.reply_document(
            document=io.BytesIO(compressed),
            filename="compressed.jpg",
            caption=(
                f"Image compressed.\n"
                f"Your image hit the gym and lost some weight. 💪\n\n"
                f"Before: {_fmt(original_size)}  →  After: {_fmt(new_size)}  ({reduction:.1f}% smaller)"
            ),
            reply_markup=MAIN_KEYBOARD,
        )
        await update.message.reply_text(
            "Anything else?",
            reply_markup=INSTAGRAM_BUTTON,
        )
    except Exception as e:
        await update.message.reply_text(f"Compression failed: {e}", reply_markup=MAIN_KEYBOARD)
        context.user_data["state"] = states.IDLE


def _fmt(b: int) -> str:
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b / (1024 * 1024):.2f} MB"
