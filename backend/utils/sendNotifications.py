import asyncio
from backend.utils.constants import TELEGRAM_GROUP_CONFIG, MAIN_GROUP_TOKEN, MAIN_GROUP_CHAT_ID
from backend.utils.telegramUtils import send_telegram_message

# Set to False to suppress all Telegram notifications (useful during testing)
TELEGRAM_ENABLED = True

def send_notifications(message, day=None):
   if not TELEGRAM_ENABLED:
      print(f"[TELEGRAM DISABLED] {message}")
      return {"specific_group_sent": False, "main_group_sent": False, "all_sent": False}
   """Helper function to send notifications to both main and specific groups"""
   specific_group_sent = None

   # First send to specific group if day is provided
   if day:
      group_cfg = TELEGRAM_GROUP_CONFIG.get(day.lower())
      if group_cfg and group_cfg.get("token") and group_cfg.get("chat_id"):
         specific_group_sent = asyncio.run(send_telegram_message(
               message,
               token=group_cfg["token"],
               chat_id=group_cfg["chat_id"]
         ))
         if not specific_group_sent:
            print(f"[TELEGRAM FAILED] Specific group notification failed for {day}")
   
   # Then always send to main group
   main_group_sent = asyncio.run(send_telegram_message(
      message,
      token=MAIN_GROUP_TOKEN,
      chat_id=MAIN_GROUP_CHAT_ID
   ))
   if not main_group_sent:
      print("[TELEGRAM FAILED] Main group notification failed")

   return {
      "specific_group_sent": specific_group_sent,
      "main_group_sent": main_group_sent,
      "all_sent": bool(main_group_sent) and (specific_group_sent is not False),
   }
