import random
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot.keyboards import MAIN_KEYBOARD
from bot.utils.user_store import register_user
from bot import states

MAX_ATTEMPTS = 3
COOLDOWN_SECONDS = 60


def _make_challenge() -> tuple[str, int, list[int]]:
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    correct = a + b

    wrongs: set[int] = set()
    while len(wrongs) < 3:
        offset = random.choice([-2, -1, 1, 2])
        c = correct + offset
        if c > 0 and c != correct:
            wrongs.add(c)

    options = list(wrongs)[:3] + [correct]
    random.shuffle(options)
    question = f"*{a} + {b} = ?*"
    return question, correct, options


def _keyboard(options: list[int]) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(f"  {o}  ", callback_data=f"verify_{o}") for o in options]
    return InlineKeyboardMarkup([buttons])


def _header(title: str, subtitle: str = "") -> str:
    lines = [
        "┌─────────────────────┐",
        f"│  🔐  {title}",
        "└─────────────────────┘",
    ]
    if subtitle:
        lines.append(f"\n_{subtitle}_")
    return "\n".join(lines)


async def send_verification(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str = "new") -> None:
    now = time.time()
    cooldown_until = context.user_data.get("verify_cooldown_until", 0)

    if now < cooldown_until:
        remaining = int(cooldown_until - now)
        await update.message.reply_text(
            f"⏳  Too many failed attempts.\n\nTry again in *{remaining}* seconds.",
            parse_mode="Markdown",
        )
        return

    context.user_data["verified"] = False
    context.user_data["verify_attempts"] = 0

    question, correct, options = _make_challenge()
    context.user_data["verify_answer"] = correct

    subtitle = "Unusual activity detected." if reason == "spam" else "Quick check before we start."

    await update.message.reply_text(
        f"🔐  *Human Verification*\n"
        f"_{subtitle}_\n\n"
        f"{question}",
        parse_mode="Markdown",
        reply_markup=_keyboard(options),
    )


async def handle_verification_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    given = int(query.data.split("_")[1])
    correct = context.user_data.get("verify_answer")
    attempts = context.user_data.get("verify_attempts", 0) + 1
    context.user_data["verify_attempts"] = attempts

    if given == correct:
        context.user_data["verified"] = True
        context.user_data["verify_attempts"] = 0
        context.user_data["_msg_times"] = []
        context.user_data["state"] = states.IDLE
        context.user_data.setdefault("image_queue", [])
        register_user(query.from_user.id)

        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Pick something from the menu below. 🐇",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    if attempts >= MAX_ATTEMPTS:
        context.user_data["verify_cooldown_until"] = time.time() + COOLDOWN_SECONDS
        context.user_data["verify_attempts"] = 0
        await query.edit_message_text(
            "┌─────────────────────┐\n"
            "│  🚫  Access Denied\n"
            "└─────────────────────┘\n\n"
            f"Too many wrong answers.\n\n"
            f"Wait *{COOLDOWN_SECONDS} seconds* then send /start to try again.",
            parse_mode="Markdown",
        )
        return

    remaining = MAX_ATTEMPTS - attempts
    question, new_correct, options = _make_challenge()
    context.user_data["verify_answer"] = new_correct

    await query.edit_message_text(
        f"🔐  *Human Verification*\n"
        f"_Wrong. {remaining} attempt(s) left._\n\n"
        f"{question}",
        parse_mode="Markdown",
        reply_markup=_keyboard(options),
    )
