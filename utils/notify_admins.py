import logging

from loader import db

async def on_startup_admins(bot):
    admins = await db.select_admins()
    for ADMIN in admins:
        try:
            await bot.send_message(chat_id=ADMIN['chat_id'], text="▶️ The bot has started")
        except Exception as err:
            logging.exception(err)
