import re
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from info import SUDO_USERS  # Only if you use it in this file

ANTILINK_ENABLED = False

async def antilink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ANTILINK_ENABLED

    user_id = update.effective_user.id

    if user_id not in SUDO_USERS:
        await update.message.reply_text("You are not allowed to use this command. ")
        return

    if not context.args:
        status = "ON 🔒" if ANTILINK_ENABLED else "OFF 🔓"
        await update.message.reply_text(f"AntiLink Status: {status}")
        return

    arg = context.args[0].lower()

    if arg == "on":
        ANTILINK_ENABLED = True
        await update.message.reply_text("🚫 AntiLink Enabled")
    elif arg == "off":
        ANTILINK_ENABLED = False
        await update.message.reply_text("✅ AntiLink Disabled")
    else:
        await update.message.reply_text("Usage: /antilink on or off")


async def anti_link_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ANTILINK_ENABLED

    if not ANTILINK_ENABLED:
        return

    if update.effective_chat.type == "private":
        return

    if not update.message or not update.message.text:
        return

    user = update.effective_user
    chat = update.effective_chat

    # ignore admins
    member = await chat.get_member(user.id)
    if member.status in ("administrator", "creator"):
        return

    text = update.message.text.lower()

    # ONLY INVITE LINKS
    patterns = [
        # Telegram invite links
        r"t\.me/\+",
        r"t\.me/joinchat",
        r"tg://join\?invite",

        # WhatsApp group invites
        r"chat\.whatsapp\.com",

        # Instagram invite/share links (not reels/posts)
        r"instagram\.com/invites",
        r"instagram\.com/direct/invite",
        r"ig\.me/",
    ]
    for pattern in patterns:
        if re.search(pattern, text):
            try:
                await update.message.delete()

                warning = await context.bot.send_message(
                    chat_id=chat.id,
                    text=(
                        f"{user.mention_html()} 🚫 <b>AntiLink Detection is Enabled</b>\n"
                        "You can't send invite links in this group."
                    ),
                    parse_mode="HTML"
                )

                await asyncio.sleep(5)

                try:
                    await warning.delete()
                except Exception:
                    pass

            except Exception as e:
                print(f"ANTILINK ERROR: {e}")

            break
