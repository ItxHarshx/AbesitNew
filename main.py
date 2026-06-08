from dotenv import load_dotenv
from telegram import Update
from telegram.ext import MessageHandler, filters
import asyncio
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import json
from info import SUDO_USERS, GROUP_ID

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mention = update.effective_user.mention_html(
        update.effective_user.first_name
    )
    bot = await context.bot.get_me()

    text = (
    f'➻ Hey <b>{mention}</b>, This is <a href="tg://user?id={bot.id}"><b>{context.bot.first_name}</b></a>, Your Abesit assistant.'
    )

    await update.message.reply_html(text)
    
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
    )
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("unpin", unpin))
    app.add_handler(CommandHandler("announce", announce))
    app.add_handler(CommandHandler("lockgroup", lockgroup))
    app.add_handler(CommandHandler("unlockgroup", unlockgroup))

    app.add_handler(
    MessageHandler(
        filters.ALL & ~filters.COMMAND,
        enforce_group_lock
    )
    )

    print("Bot is running...")

    app.run_polling()

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:

        mention = user.mention_html(user.first_name)

        msg = await update.message.reply_html(
            f"Hello {mention}, welcome to ABESIT Batch (2026-2027). wishing you a great college journey! 🎉"
        )

        await asyncio.sleep(300)  # 5 minutes

        try:
            await msg.delete()
        except:
            pass

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    member = await chat.get_member(user.id)

    if member.status not in ["administrator", "creator"]:
        return

    if not update.message.reply_to_message:
        msg = await update.message.reply_text(
            "Reply to a message to pin it."
        )

        await asyncio.sleep(5)

        try:
            await msg.delete()
        except:
            pass

        return

    await update.message.reply_to_message.pin(
        disable_notification=True
    )

    msg = await update.message.reply_text(
        "Message pinned."
    )

    await asyncio.sleep(5)

    try:
        await msg.delete()
    except:
        pass

async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    member = await chat.get_member(user.id)

    if member.status not in ["administrator", "creator"]:
        return

    await chat.unpin_all_messages()

    msg = await update.message.reply_text(
        "Message unpinned."
    )

    await asyncio.sleep(5)

    try:
        await msg.delete()
    except:
        pass

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
        await update.message.reply_text(
        "Announcements can only be made from my DM."
    )
        return

    # DM only
    if update.effective_chat.type != "private":
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
        "<b>📢 ANNOUNCEMENT !</b>\n\n"
        f"{announcement}\n\n"
        "<b>- ABESIT Assistant.</b>"
    ),
    parse_mode="HTML"
        )

    await msg.pin(disable_notification=True)

    await update.message.reply_text(
        "Announcement posted and pinned."
    )


LOCK_FILE = "lock_state.json"


def get_lock_state():
    try:
        with open(LOCK_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"group_locked": False}


def set_lock_state(locked: bool):
    with open(LOCK_FILE, "w") as f:
        json.dump({"group_locked": locked}, f)

async def lockgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in SUDO_USERS:
        await update.message.reply_text(
            "Only official admins can use this command."
        )
        return

    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "This command can only be used in a group."
        )
        return

    set_lock_state(True)

    await update.message.reply_text(
        "🔒 Group Lock Enabled\n\n"
        "Only group admins can send messages until the group is unlocked."
    )

async def unlockgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in SUDO_USERS:
        await update.message.reply_text(
            "Only official admins can use this command."
        )
        return

    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "This command can only be used in a group."
        )
        return

    set_lock_state(False)

    await update.message.reply_text(
        "🔓 Group Lock Disabled\n\n"
        "Members can send messages again."
    )

async def enforce_group_lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("LOCK HANDLER RUNNING")
    # Ignore messages without a sender
    if not update.effective_user:
        return

    # Ignore private chats
    if update.effective_chat.type == "private":
        return

    # Check lock status
    if not get_lock_state()["group_locked"]:
        return

    user = update.effective_user
    chat = update.effective_chat

    member = await chat.get_member(user.id)

    # Allow admins and owners
    if member.status in ["administrator", "creator"]:
        return

    try:
        await update.message.delete()
    except:
        pass




if __name__ == "__main__":
    main()
