import re
import os
import uuid
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

URL_PATTERN = re.compile(
    r"(https?://(?:www\.)?(?:instagram\.com/reel[s]?/\S+|youtube\.com/shorts/\S+|youtu\.be/\S+))"
)

async def insyt_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    match = URL_PATTERN.search(text)
    if not match:
        return

    url = match.group(1)
    chat_id = update.effective_chat.id
    filename = f"{uuid.uuid4()}.mp4"

    status_msg = await update.message.reply_text("Downloading...")

    ydl_opts = {
        "outtmpl": filename,
        "format": "mp4/bestvideo+bestaudio",
        "quiet": True,
        "merge_output_format": "mp4",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open(filename, "rb") as video_file:
            await context.bot.send_video(chat_id=chat_id, video=video_file)

    except Exception as e:
        await update.message.reply_text(f"Failed to download: {e}")

    finally:
        await status_msg.delete()
        if os.path.exists(filename):
            os.remove(filename)
