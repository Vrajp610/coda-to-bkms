import os
from telegram import Bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_message(message: str):
    """Send a message to a Telegram chat."""
    if not TOKEN or not CHAT_ID:
        raise ValueError("Telegram TOKEN or CHAT_ID is not set in environment variables.")
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)