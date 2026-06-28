import re
from telegram import Update
from telegram.ext import ContextTypes

INSTAGRAM_REEL = re.compile(
    r"https?://(?:www\.)?instagram\.com/reel/[\w-]+"
)

YOUTUBE_SHORT = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com/shorts/|youtu\.be/)[^\s]+"
)


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if INSTAGRAM_REEL.search(text):
        await update.message.reply_text(
            "Instagram Reel detected..."
        )
        return

    if YOUTUBE_SHORT.search(text):
        if "/shorts/" in text:
            await update.message.reply_text(
                "YouTube Short detected..."
            )
