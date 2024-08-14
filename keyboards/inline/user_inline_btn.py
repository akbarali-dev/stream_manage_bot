from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.callback_data import MyCallback


def battle_data(battles):
    column = []
    for c in battles:
        # column.append([InlineKeyboardButton(text=c['name'], callback_data=c['id'])])
        column.append([InlineKeyboardButton(text=c['name'],
                                            callback_data=MyCallback(foo='select_competition', bar=c['id']).pack())])
    battle_menu = InlineKeyboardMarkup(row_width=1, inline_keyboard=column)
    return battle_menu


def battle_data_link(link, sport_type_id):
    column = []
    if link:
        column.append([InlineKeyboardButton(text="Jonli efirga o'tish", url=link)])
    column.append([InlineKeyboardButton(text="Orqaga", callback_data=MyCallback(foo='back', bar=sport_type_id).pack())])
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=column)
