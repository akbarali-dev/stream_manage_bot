from aiogram import types
from aiogram.filters import Filter
from aiogram.types import Message

from loader import db


class SportTypeFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        nn = await db.already_exists_sport_type(message.text)
        return nn['result']
