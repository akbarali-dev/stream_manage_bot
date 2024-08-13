from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def battle_data(battles):
    column = []
    for c in battles:
        column.append([InlineKeyboardButton(text=c['name'], callback_data=c['id'])])
    battle_menu = InlineKeyboardMarkup(row_width=1, inline_keyboard=column)
    return battle_menu
