import io
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.utils.remove_bg import remove_background
from bot.keyboards import MAIN_KEYBOARD, CANCEL_KEYBOARD, INSTAGRAM_BUTTON
from bot import states


async def start_remove_bg_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = states.AWAIT_REMOVE_BG
    await update.message.reply_text(
        "Send me the image and I'll remove the background.\n"
        "Works best with a clear subject and decent contrast.",
        reply_markup=CANCEL_KEYBOARD,
    )


async def do_remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)

    try:
        result_bytes = remove_background(image_bytes)
        context.user_data["state"] = states.IDLE

        await update.message.reply_document(
            document=io.BytesIO(result_bytes),
            filename="no_background.png",
            caption=(
                "Background removed.\n"
                "Clean cut, zero effort. 🪄"
            ),
            reply_markup=MAIN_KEYBOARD,
        )
        await update.message.reply_text(
            "Anything else?",
            reply_markup=INSTAGRAM_BUTTON,
        )
    except Exception as e:
        await update.message.reply_text(f"Something went wrong: {e}", reply_markup=MAIN_KEYBOARD)
        context.user_data["state"] = states.IDLE
