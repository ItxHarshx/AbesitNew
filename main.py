from dotenv import load_dotenv
from telegram import Update
from telegram.ext import MessageHandler, filters
import asyncio
from telegram.ext import Application, CommandHandler, ContextTypes
import os
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
    if user_id not in SUDO_USERS:
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



if __name__ == "__main__":
    main()
