import io
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.utils.resize_image import resize_image, parse_dimensions
from bot.keyboards import MAIN_KEYBOARD, CANCEL_KEYBOARD, INSTAGRAM_BUTTON
from bot import states


async def start_resize_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["state"] = states.AWAIT_RESIZE_IMAGE
    await update.message.reply_text(
        "Send me the image you want to resize.",
        reply_markup=CANCEL_KEYBOARD,
    )


async def image_received(update: Update, context: ContextTypes.DEFAULT_TYPE, image_bytes: bytes) -> None:
    context.user_data["resize_image"] = image_bytes
    context.user_data["state"] = states.AWAIT_RESIZE_DIMS
    await update.message.reply_text(
        "Got it. Now tell me the target size.\n\n"
        "Examples:\n"
        "800x600  — specific dimensions in pixels\n"
        "50%  — scale to 50% of original size",
        reply_markup=CANCEL_KEYBOARD,
    )


async def do_resize(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    image_bytes = context.user_data.get("resize_image")
    if not image_bytes:
        await update.message.reply_text("No image found. Please start over.", reply_markup=MAIN_KEYBOARD)
        context.user_data["state"] = states.IDLE
        return

    from PIL import Image
    orig = Image.open(io.BytesIO(image_bytes))
    orig_w, orig_h = orig.size

    try:
        width, height = parse_dimensions(text, orig_w, orig_h)
    except ValueError as e:
        await update.message.reply_text(
            f"{e}\n\nExamples: 800x600 or 50%"
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)

    try:
        resized_bytes, ow, oh, nw, nh = resize_image(image_bytes, width, height)
        context.user_data["state"] = states.IDLE
        context.user_data.pop("resize_image", None)

        await update.message.reply_document(
            document=io.BytesIO(resized_bytes),
            filename="resized.jpg",
            caption=(
                f"Resized and ready.\n"
                f"{ow}x{oh}  →  {nw}x{nh} pixels"
            ),
            reply_markup=MAIN_KEYBOARD,
        )
        await update.message.reply_text(
            "Anything else?",
            reply_markup=INSTAGRAM_BUTTON,
        )
    except Exception as e:
        await update.message.reply_text(f"Resize failed: {e}", reply_markup=MAIN_KEYBOARD)
        context.user_data["state"] = states.IDLE
