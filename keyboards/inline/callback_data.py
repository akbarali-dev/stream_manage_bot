from aiogram.filters.callback_data import CallbackData


class MyCallback(CallbackData, prefix="my"):
    foo: str
    bar: str
