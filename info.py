from telegram import Update
from telegram.ext import ContextTypes

SUDO_USERS = [
    6418418064, 8478458752, # Your Telegram ID 8478458752
]

GROUP_ID = -1004205157170

async def id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        await message.reply_text(
            f"👤 <b>This User's ID:</b> <code>{user.id}</code>",
            parse_mode="HTML"
        )
    else:
        user = update.effective_user
        await message.reply_text(
            f"👤 <b>Your ID:</b> <code>{user.id}</code>",
            parse_mode="HTML"
        )


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    await update.message.reply_text(
        f"💬 <b>Chat ID:</b> <code>{chat.id}</code>",
        parse_mode="HTML"
    )
