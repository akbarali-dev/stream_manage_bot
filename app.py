import asyncio
import logging
import sys

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from loader import dp, bot, db
from handlers.users.start import command_start_handler
from utils.notify_admins import on_startup_admins
from utils.set_bot_commands import set_default_commands


# All handlers should be attached to the Router (or Dispatcher)

async def on_startup():
    await db.create()
    await set_default_commands(bot)
    await on_startup_admins(bot)
    asyncio.create_task(db.listen('data_change'))


async def main() -> None:
    # bot.send_photo(parse_mode=)
    dp.message.once = False

    await on_startup()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
