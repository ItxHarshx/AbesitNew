import os
import re
import asyncio
import yt_dlp

from telegram import Update
from telegram.ext import ContextTypes

INSTAGRAM_REEL = re.compile(
    r"https?://(?:www\.)?instagram\.com/reel/[\w-]+"
)


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    match = INSTAGRAM_REEL.search(text)
    if not match:
        return

    url = match.group(0)

    status = await update.message.reply_text("⏬ Downloading Reel...")

    try:
        video = await asyncio.to_thread(download_reel, url)

        await update.message.reply_video(
            video=open(video, "rb"),
            supports_streaming=True,
            caption=f"🎬 Shared by {update.effective_user.mention_html()}",
            parse_mode="HTML"
        )

        os.remove(video)
        await status.delete()

    except Exception as e:
        print(e)
        await status.edit_text("❌ Failed to download reel.")

def download_reel(url):
    ydl_opts = {
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True,
    }

    os.makedirs("downloads", exist_ok=True)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
