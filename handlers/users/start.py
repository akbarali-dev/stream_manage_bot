from typing import Text

from loader import dp, bot, db
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import html


from filters.admin_filters import AdminFilter
from aiogram import F
from keyboards.default.user_btn import question_btn


@dp.message(CommandStart())
@dp.message(F.text == '🏠Asosiy menu')
async def command_start_handler(message: Message) -> None:
    sport_types = await db.sport_types()
    msg = "Quyidagi sport musobaqalaridan birini tanlang"
    await message.answer(msg, reply_markup=question_btn(sport_types), parse_mode="html")
