from backend.utils.postgresConn import get_config_value

async def send_telegram_message(message: str, token: str = None, chat_id: str = None) -> bool:
    """Send a message to a Telegram chat.
    If token/chat_id are omitted, use MAIN_GROUP_TELEGRAM_TOKEN and MAIN_GROUP_TELEGRAM_CHAT_ID from env.
    Returns True on success, False on failure.
    """
    from telegram import Bot

    token = token or get_config_value("MAIN_GROUP_TELEGRAM_TOKEN")
    chat_id = chat_id or get_config_value("MAIN_GROUP_TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise ValueError("Telegram TOKEN or CHAT_ID is not set in environment variables or arguments.")
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception:
        return False