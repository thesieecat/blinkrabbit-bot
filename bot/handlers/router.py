from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from bot import states
from bot.keyboards import (
    MAIN_KEYBOARD, BTN_PDF, BTN_COMPRESS, BTN_QR,
    BTN_PASSPORT, BTN_RESIZE, BTN_HELP,
    BTN_GENERATE_PDF, BTN_CLEAR_IMAGES, BTN_CANCEL, BTN_REMOVE_BG,
)
from bot.handlers import (
    pdf_handler,
    compress_handler,
    qr_handler,
    passport_handler,
    resize_handler,
    remove_bg_handler,
)
from bot.handlers.start import help_command
from bot.utils.user_store import register_user
from bot.utils.rate_limiter import record_message


async def _check_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not context.user_data.get("verified"):
        await update.message.reply_text(
            "Please complete the verification first. Send /start to begin."
        )
        return False
    if record_message(context.user_data):
        context.user_data["verified"] = False
        context.user_data["_msg_times"] = []
        from bot.handlers.verification_handler import send_verification
        await send_verification(update, context, reason="spam")
        return False
    return True


async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update, context):
        return
    register_user(update.effective_chat.id)
    text = update.message.text
    state = context.user_data.get("state", states.IDLE)

    if text == BTN_PDF:
        await pdf_handler.start_pdf_mode(update, context)
        return
    if text == BTN_COMPRESS:
        await compress_handler.start_compress_mode(update, context)
        return
    if text == BTN_QR:
        await qr_handler.start_qr_mode(update, context)
        return
    if text == BTN_PASSPORT:
        await passport_handler.start_passport_mode(update, context)
        return
    if text == BTN_RESIZE:
        await resize_handler.start_resize_mode(update, context)
        return
    if text == BTN_REMOVE_BG:
        await remove_bg_handler.start_remove_bg_mode(update, context)
        return
    if text == BTN_HELP:
        await help_command(update, context)
        return
    if text == BTN_GENERATE_PDF:
        await pdf_handler.generate_pdf(update, context)
        return
    if text == BTN_CLEAR_IMAGES:
        await pdf_handler.clear_images(update, context)
        return
    if text == BTN_CANCEL:
        context.user_data["state"] = states.IDLE
        context.user_data.pop("resize_image", None)
        await update.message.reply_text(
            "Cancelled. What would you like to do?",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    if state == states.AWAIT_QR_TEXT:
        await qr_handler.do_qr(update, context, text)
        return
    if state == states.AWAIT_RESIZE_DIMS:
        await resize_handler.do_resize(update, context, text)
        return

    await update.message.reply_text(
        "Use the menu below to get started.",
        reply_markup=MAIN_KEYBOARD,
    )


async def route_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update, context):
        return
    register_user(update.effective_chat.id)
    state = context.user_data.get("state", states.IDLE)

    photo = update.message.photo[-1] if update.message.photo else None
    document = update.message.document

    file_obj = None
    if photo:
        file_obj = await photo.get_file()
    elif document and document.mime_type and document.mime_type.startswith("image/"):
        file_obj = await document.get_file()

    if not file_obj:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    raw = await file_obj.download_as_bytearray()
    image_bytes = bytes(raw)

    context.user_data["last_image"] = image_bytes

    if state == states.AWAIT_PDF_IMAGES:
        await pdf_handler.queue_image(update, context, image_bytes)
    elif state == states.AWAIT_COMPRESS:
        await compress_handler.do_compress(update, context, image_bytes)
    elif state == states.AWAIT_PASSPORT:
        await passport_handler.do_passport(update, context, image_bytes)
    elif state == states.AWAIT_RESIZE_IMAGE:
        await resize_handler.image_received(update, context, image_bytes)
    elif state == states.AWAIT_REMOVE_BG:
        await remove_bg_handler.do_remove_bg(update, context, image_bytes)
    else:
        await update.message.reply_text(
            "Image received. What do you want to do with it?",
            reply_markup=MAIN_KEYBOARD,
        )
