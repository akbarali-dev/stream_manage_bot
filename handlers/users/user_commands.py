from typing import Text
from aiogram.filters import command

from loader import dp, db
from aiogram.types import Message
from aiogram.types.input_file import InputFile
from aiogram import html

from aiogram.filters import Command
from filters.sport_type_filter import SportTypeFilter
from aiogram import types
from keyboards.inline.user_inline_btn import battle_data


@dp.message(SportTypeFilter())
async def select_sport_battle(message: Message) -> None:
    competitions = await db.select_competitions_by_sport_type(name=message.text)
    image = await db.sport_type_image(name=message.text)
    print(competitions)
    print(image['file_id'])
    await message.answer_photo(photo=image['file_id'],
        caption="Choose one of the competitions below", reply_markup=battle_data(competitions))
