import os
import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_instagram_video(url: str) -> str | None:
    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
            "format": "mp4/best",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if not info:
                return None

            # file path
            file_path = ydl.prepare_filename(info)

            # sometimes extension changes, ensure correct file exists
            if os.path.exists(file_path):
                return file_path

            # fallback search
            base = os.path.splitext(file_path)[0]
            for ext in ["mp4", "mkv", "webm"]:
                alt = base + "." + ext
                if os.path.exists(alt):
                    return alt

            return None

    except Exception as e:
        print("yt-dlp error:", e)
        return None


async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()

    if "instagram.com" not in url:
        return

    status = await update.message.reply_text("⏳ Downloading via yt-dlp...")

    file_path = download_instagram_video(url)

    if not file_path:
        await status.edit_text("❌ Download failed. Try another link.")
        return

    await status.edit_text("📤 Uploading...")

    try:
        await update.message.reply_video(
            video=open(file_path, "rb"),
            supports_streaming=True
        )

        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Upload failed: {e}")
