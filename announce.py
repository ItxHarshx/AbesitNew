from telegram import Update
from telegram.ext import ContextTypes

from info import SUDO_USERS, GROUP_ID


async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Sudo check
    # Sudo check
    if user_id not in SUDO_USERS:
        await update.message.reply_text(
        "Only official admins are allowed to make announcements."
    )
        return

    # DM only
    if update.effective_chat.type != "private":
        await update.effective_chat.send_message(
        "Announcements can only be made from my DM."
    )
        return

    # Message check
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/announce Your announcement here"
        )
        return

    announcement = " ".join(context.args)

    msg = await context.bot.send_message(
        chat_id=GROUP_ID,
    text=(
        "<b>📢 Announcement!</b>\n\n"
        f"{announcement}\n\n"
        "<b>- ABESIT Assistant.</b>"
    ),
    parse_mode="HTML"
        )

    await msg.pin(disable_notification=True)

    await update.message.reply_text(
        "Announcement posted and pinned."
    )
