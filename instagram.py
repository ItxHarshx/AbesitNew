import time
import httpx
from telegram import Update, InputFile
from telegram.ext import ContextTypes
import os

API_URL = "https://instagram-reels-downloader-api.p.rapidapi.com/download"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


async def fetch_insta_media(link: str):
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "instagram-reels-downloader-api.p.rapidapi.com",
        "Content-Type": "application/json",
    }

    params = {
        "url": link,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                API_URL,
                headers=headers,
                params=params,
            )

            if response.status_code != 200:
                return None

            data = response.json()

            if not data.get("success"):
                return None

            if not data.get("data"):
                return None

            if not data["data"].get("medias"):
                return None

            return data

    except Exception:
        return None


async def download_with_progress(url: str, progress_msg, label: str) -> bytes | None:
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    return None

                total = int(response.headers.get("content-length", 0))
                if total == 0:
                    return None

                data = bytearray()
                downloaded = 0
                start = time.time()
                last_update = 0

                async for chunk in response.aiter_bytes(64 * 1024):
                    data.extend(chunk)
                    downloaded += len(chunk)

                    now = time.time()

                    if now - last_update >= 2:
                        last_update = now

                        percent = int(downloaded * 100 / total)
                        elapsed = now - start
                        eta = (total - downloaded) * elapsed / downloaded if downloaded else 0

                        try:
                            await progress_msg.edit_text(
                                f"{label} {percent}% | ETA: {int(eta)}s"
                            )
                        except Exception:
                            pass

                return bytes(data)

    except Exception:
        return None


async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    link = update.message.text.strip()

    if "instagram.com" not in link:
        return

    status = await update.message.reply_text("⏳ Fetching media...")

    data = await fetch_insta_media(link)

    if not data:
        await status.edit_text("❌ Could not retrieve media.")
        return

    medias = data["data"]["medias"]
    
    video_url = None
    
    for media in medias:
        if media.get("type") == "video":
            video_url = media.get("url")
            break
            
    if not video_url:
        await status.edit_text("❌ No video found.")
        return

    await status.edit_text("📥 Downloading...")

    media = await download_with_progress(video_url, status, "📥")

    if not media:
        await status.edit_text("❌ Download failed.")
        return

    await status.edit_text("📤 Uploading...")

    await update.message.reply_video(
        video=InputFile(media, filename=f"instagram_{update.message.message_id}.mp4")
    )

    await status.delete()
