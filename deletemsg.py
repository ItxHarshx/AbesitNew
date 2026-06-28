from telegram import Update
from telegram.ext import ContextTypes


async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("This command can only be used in groups.")
        return

    member = await chat.get_member(user.id)
    if member.status not in ("administrator", "creator"):
        await update.message.reply_text("❌ You need admin rights to use this command.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message to delete it.")
        return

    try:
        await update.message.reply_to_message.delete()
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(f"❌ Failed:\n{e}")
