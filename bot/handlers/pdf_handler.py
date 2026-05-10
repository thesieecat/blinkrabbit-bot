import io
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.utils.image_to_pdf import images_to_pdf
from bot.keyboards import MAIN_KEYBOARD, PDF_KEYBOARD, INSTAGRAM_BUTTON
from bot import states


async def start_pdf_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = states.AWAIT_PDF_IMAGES
    context.user_data.setdefault("image_queue", [])
    await update.message.reply_text(
        "Send me the images you want in the PDF.\n"
        "You can send multiple — I'll queue them in order. Tap Generate PDF when ready.",
        reply_markup=PDF_KEYBOARD,
    )


async def queue_image(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes) -> None:
    context.user_data.setdefault("image_queue", [])
    context.user_data["image_queue"].append(image_bytes)
    count = len(context.user_data["image_queue"])
    await update.message.reply_text(
        f"Image {count} added. Send more or tap Generate PDF.",
        reply_markup=PDF_KEYBOARD,
    )


async def generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    queue = context.user_data.get("image_queue", [])
    if not queue:
        await update.message.reply_text(
            "Nothing queued yet. Send some images first.",
            reply_markup=PDF_KEYBOARD,
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)

    try:
        pdf_bytes = images_to_pdf(queue)
        context.user_data["image_queue"] = []
        context.user_data["state"] = states.IDLE

        await update.message.reply_document(
            document=io.BytesIO(pdf_bytes),
            filename="output.pdf",
            caption=(
                f"Your PDF is ready.\n"
                f"BlinkRabbit worked its magic on {len(queue)} image(s). 🐇"
            ),
            reply_markup=MAIN_KEYBOARD,
        )
        await update.message.reply_text(
            "Anything else?",
            reply_markup=INSTAGRAM_BUTTON,
        )
    except Exception as e:
        await update.message.reply_text(f"Something went wrong: {e}\nTry again?", reply_markup=PDF_KEYBOARD)


async def clear_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    count = len(context.user_data.get("image_queue", []))
    context.user_data["image_queue"] = []
    await update.message.reply_text(
        f"Cleared {count} image(s). Send new ones whenever you're ready.",
        reply_markup=PDF_KEYBOARD,
    )
