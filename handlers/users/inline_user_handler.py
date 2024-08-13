from loader import dp
from aiogram.types import CallbackQuery
from aiogram import Router, F

router = Router()


@dp.callback_query()
async def inline_user_handler(query: CallbackQuery):
    print(query.data)
    await query.message.answer("salomm")
