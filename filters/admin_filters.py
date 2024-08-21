from aiogram import types
from aiogram.filters import Filter
from aiogram.types import Message
from loader import db


class AdminFilter(Filter):


    async def __call__(self, message: Message) -> bool:
        admins = await db.select_admins()
        for admin in admins:
            if admin['chat_id'] == message.chat.id:
                return True
            return False


