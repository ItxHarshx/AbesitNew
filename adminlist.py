from telegram import Update
from telegram.ext import ContextTypes

async def adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text(
            "This command can only be used in groups."
        )
        return

    admins = await chat.get_administrators()

    owner = None
    admin_list = []

    for admin in admins:
        user = admin.user

        # clickable mention only (NO username)
        mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

        if admin.status == "creator":
            owner = mention
        else:
            admin_list.append(mention)

    text = "<b>👑 Admin List</b>\n\n"

    # OWNER FIRST
    if owner:
        text += f"<b>👑 Owner:</b>\n{owner}\n\n"
    else:
        text += "<b>👑 Owner:</b> Not found\n\n"

    # ADMINS LIST
    if admin_list:
        text += "<b>🛡 Admins:</b>\n"
        text += "\n".join([f"• {a}" for a in admin_list])
    else:
        text += "<b>🛡 Admins:</b> None"

    await update.message.reply_html(text)
