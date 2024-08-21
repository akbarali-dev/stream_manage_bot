from typing import Text

from loader import dp, bot, db
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import html
import asyncpg

from aiogram import F
from keyboards.default.user_btn import question_btn
from keyboards.inline.user_inline_btn import channel_btns


async def try_add_user(full_name: str, chat_id: int) -> None:
    try:
        await db.add_user(full_name, chat_id)
    except asyncpg.exceptions.UniqueViolationError:
        pass


@dp.message(CommandStart())
@dp.message(F.text == '🏠Asosiy menu')
async def command_start_handler(message: Message) -> None:
    await try_add_user(message.from_user.full_name, message.chat.id)
    channels = await db.select_all_channel()
    if channels:
        msg1 = "Tavsiya etilgan kanallar"
        await message.answer(msg1, reply_markup=channel_btns(channels))
    sport_types = await db.sport_types()
    msg2 = "Quyidagi sport musobaqalaridan birini tanlang"

    await message.answer(msg2, reply_markup=question_btn(sport_types), parse_mode="html")
