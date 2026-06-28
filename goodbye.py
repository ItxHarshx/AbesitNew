# goodbye.py

from telegram import Update
from telegram.ext import ContextTypes

# optional: fixed message
GOODBYE_TEXT = "👋 {name} left the chat."


async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.left_chat_member:
        return

    user = message.left_chat_member

    # ignore bot itself
    if user.id == context.bot.id:
        return

    text = GOODBYE_TEXT.format(name=user.mention_html())

    await context.bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_to_message_id=message.message_id,
    )
