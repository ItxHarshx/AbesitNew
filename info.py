from telegram import Update
from telegram.ext import ContextTypes

SUDO_USERS = [
    6418418064, 8478458752, # Your Telegram ID 8478458752
]

GROUP_ID = -1004205157170


async def id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # If replying to someone
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        await message.reply_text(
            f"👤 User ID: {user.id}\n"
            f"Name: {user.first_name}"
        )
    else:
        # Own ID
        user = update.effective_user
        await message.reply_text(
            f"👤 Your ID: {user.id}"
        )

async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    await update.message.reply_text(
        f"💬 Chat ID: {chat.id}\n"
        f"Type: {chat.type}"
    )
