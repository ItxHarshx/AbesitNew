from dotenv import load_dotenv
from telegram import Update
from telegram.ext import MessageHandler, filters
import asyncio
from telegram.ext import Application, CommandHandler, ContextTypes
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mention = update.effective_user.mention_html(
        update.effective_user.first_name
    )
    bot = await context.bot.get_me()

    text = (
    f"✦ Hey <b>{mention}</b> !\n\n"
    f'◎ This is <a href="tg://user?id={bot.id}"><b>{context.bot.first_name}</b></a>, Your Abesit assistant.'
    )

    await update.message.reply_html(text)
    
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
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


if __name__ == "__main__":
    main()
