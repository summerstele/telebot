import os
import uuid
import logging
import nest_asyncio
import asyncio
import yt_dlp

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Apply event loop fix for macOS
nest_asyncio.apply()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace this with your bot token
TELEGRAM_BOT_TOKEN = "7597983353:AAF3hR-roVLxWAyk-fui5gE7zcvHWKGuL4k"

# Download function
def download_reel(url):
    filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        "outtmpl": filename,
        "format": "best",
        "merge_output_format": "mp4",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return filename
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me an Instagram reel link to download.")

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "instagram.com/reel" not in url:
        await update.message.reply_text("❗️Please send a valid Instagram reel URL.")
        return

    await update.message.chat.send_action(ChatAction.UPLOAD_VIDEO)
    await update.message.reply_text("📥 Downloading...")

    file_path = download_reel(url)

    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "rb") as video:
                await update.message.reply_video(video)
        except Exception as e:
            await update.message.reply_text("⚠️ Could not send the video.")
            logger.error(f"Send error: {e}")
        finally:
            os.remove(file_path)
    else:
        await update.message.reply_text("❌ Failed to download the reel.")

# Bot entrypoint
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    await app.run_polling()

# Run
if __name__ == "__main__":
    asyncio.run(main())
