from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from middlewares import middleware_add
from data.config import BOT_TOKEN
from utils.db_api.postgresql import Database


from apscheduler.schedulers.asyncio import AsyncIOScheduler

dp = Dispatcher(skip_updates=True)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
middleware_add(dp, bot)
db = Database()
