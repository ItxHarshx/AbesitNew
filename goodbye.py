from telegram import Update
from telegram.ext import ContextTypes


async def member_left(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fires when a service message reports a user left/was removed."""
    left_user = update.message.left_chat_member
    if left_user is None:
        return

    name = left_user.full_name  # first_name + last_name if present
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{name} left the group",
    )
