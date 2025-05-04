from telegram import Bot

# Get sensitive data from environment variables
TOKEN = '8008353281:AAGKOYWJ9Hb5t8ilMQ4i2d3Z3g-0WGC5oLE'
CHAT_ID = '-1001570996136'

async def send_telegram_message(message: str):
    """Send a message to a Telegram chat."""
    if not TOKEN or not CHAT_ID:
        raise ValueError("Telegram TOKEN or CHAT_ID is not set in environment variables.")
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)