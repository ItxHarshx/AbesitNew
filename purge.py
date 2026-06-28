import asyncio
from telegram import Update
from telegram.ext import ContextTypes


async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❌ This command works only in groups.")
        return

    # Admin check
    try:
        member = await chat.get_member(user.id)
        if member.status not in ("administrator", "creator"):
            await update.message.reply_text("❌ You need admin rights to use /purge.")
            return
    except Exception:
        return

    # ---------------------------
    # MODE 1: Reply-based purge
    # ---------------------------
    if update.message.reply_to_message:
        start_msg_id = update.message.reply_to_message.message_id
        end_msg_id = update.message.message_id

        deleted = 0

        # Telegram allows deleting message by ID one by one (safe loop)
        for msg_id in range(start_msg_id, end_msg_id + 1):
            try:
                await context.bot.delete_message(chat.id, msg_id)
                deleted += 1
                await asyncio.sleep(0.03)  # small delay to avoid flood limit
            except Exception:
                pass  # ignore already deleted / protected messages

        return

    # ---------------------------
    # MODE 2: /purge 10 (last N messages)
    # ---------------------------
    if context.args and context.args[0].isdigit():
        limit = min(int(context.args[0]), 100)  # safety limit max 100

        deleted = 0
        current_id = update.message.message_id

        for i in range(limit):
            try:
                await context.bot.delete_message(chat.id, current_id - i)
                deleted += 1
                await asyncio.sleep(0.03)
            except Exception:
                pass

        return

    # ---------------------------
    # NO VALID INPUT
    # ---------------------------
    await update.message.reply_text(
        "⚠️ Usage:\n"
        "• Reply to a message and use /purge\n"
        "• /purge 10 (delete last 10 messages)"
    )
