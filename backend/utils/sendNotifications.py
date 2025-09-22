import asyncio
from backend.utils.constants import TELEGRAM_GROUP_CONFIG, MAIN_GROUP_TOKEN, MAIN_GROUP_CHAT_ID
from backend.utils.telegramUtils import send_telegram_message

def send_notifications(message, day=None):
   """Helper function to send notifications to both main and specific groups"""
   # First send to specific group if day is provided
   if day:
      group_cfg = TELEGRAM_GROUP_CONFIG.get(day.lower())
      if group_cfg and group_cfg.get("token") and group_cfg.get("chat_id"):
         asyncio.run(send_telegram_message(
               message,
               token=group_cfg["token"],
               chat_id=group_cfg["chat_id"]
         ))
   
   # Then always send to main group
   asyncio.run(send_telegram_message(
      message,
      token=MAIN_GROUP_TOKEN,
      chat_id=MAIN_GROUP_CHAT_ID
   ))