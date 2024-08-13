from loader import dp, bot, db
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import html

from aiogram.filters import Command
from filters.admin_filters import AdminFilter
from aiogram import types
from keyboards.default.user_btn import question_btn


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    sport_types = await db.sport_types()
    # ChatFullInfo = await bot.get_chat(chat_id='@akbarali_for_test_channel')
    # print(ChatFullInfo)
    msg = "Quyidagi sport musobaqalaridan birini tanlang"
    await message.answer(msg, reply_markup=question_btn(sport_types), parse_mode="html")
