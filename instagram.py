import os
import logging
import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Path to a cookies.txt file exported from a logged-in Instagram session.
# This is required for most reels to download reliably. See notes below.
COOKIES_FILE = "instagram_cookies.txt"


def download_instagram_video(url: str) -> tuple[str | None, str | None]:
    """Returns (file_path, error_message). file_path is None on failure."""
    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True,
        "noprogress": True,
        "retries": 3,
        "socket_timeout": 30,
    }

    if os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None, "No info extracted from URL."

            file_path = ydl.prepare_filename(info)

            if os.path.exists(file_path):
                return file_path, None

            base = os.path.splitext(file_path)[0]
            for ext in ["mp4", "mkv", "webm"]:
                alt = f"{base}.{ext}"
                if os.path.exists(alt):
                    return alt, None

            return None, "File not found after download."

    except yt_dlp.utils.DownloadError as e:
        logger.error("yt-dlp DownloadError for %s: %s", url, e)
        return None, str(e)
    except Exception as e:
        logger.exception("Unexpected error downloading %s", url)
        return None, str(e)


async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()
    if "instagram.com" not in url:
        return

    status = await update.message.reply_text("⏳ Downloading via yt-dlp...")

    file_path, error = download_instagram_video(url)

    if not file_path:
        # Show the REAL reason instead of a generic message
        short_error = (error or "unknown error")[:300]
        await status.edit_text(f"❌ Download failed:\n`{short_error}`", parse_mode="Markdown")
        return

    await status.edit_text("📤 Uploading...")

    try:
        with open(file_path, "rb") as video_file:
            await update.message.reply_video(
                video=video_file,
                supports_streaming=True,
            )
        await status.delete()
    except Exception as e:
        logger.exception("Upload failed for %s", file_path)
        await status.edit_text(f"❌ Upload failed: {e}")
    finally:
        # Clean up downloaded file to avoid filling disk
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass
