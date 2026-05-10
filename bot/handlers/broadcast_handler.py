import os
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import Forbidden, BadRequest
from bot.utils.user_store import get_all_users, user_count


def _is_admin(chat_id: int) -> bool:
    admin_id = os.environ.get("ADMIN_CHAT_ID", "")
    return str(chat_id) == admin_id


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    if not _is_admin(chat_id):
        await update.message.reply_text("You are not authorised to use this command.")
        return

    if not context.args:
        total = user_count()
        await update.message.reply_text(
            f"Usage: /broadcast <message>\n\n"
            f"Total registered users: {total}"
        )
        return

    message_text = " ".join(context.args)
    users = get_all_users()

    if not users:
        await update.message.reply_text("No users registered yet.")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    status_msg = await update.message.reply_text(
        f"Sending to {len(users)} user(s)..."
    )

    sent = 0
    failed = 0

    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=message_text,
                parse_mode="Markdown",
            )
            sent += 1
        except (Forbidden, BadRequest):
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"Broadcast complete.\n\n"
        f"Delivered: {sent}\n"
        f"Failed: {failed}"
    )
