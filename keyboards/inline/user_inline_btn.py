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

def channel_btns(channel):
    column = []
    for c in channel:
        # column.append([InlineKeyboardButton(text=c['name'], callback_data=c['id'])])
        column.append([InlineKeyboardButton(text="🔘"+c['name'], url="https://t.me/"+c['username']),])
    battle_menu = InlineKeyboardMarkup(row_width=1, inline_keyboard=column)
    return battle_menu

def battle_data_link(link, sport_type_id):
    column = []
    if link:
        column.append([InlineKeyboardButton(text="Go live 🎥" , url=link)])
    column.append([InlineKeyboardButton(text="⬅️  Bak", callback_data=MyCallback(foo='back', bar=sport_type_id).pack())])
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=column)

def stream_link(link):
    column = []
    if link:
        column.append([InlineKeyboardButton(text="Go live 🎥", url=link)])
        return InlineKeyboardMarkup(row_width=1, inline_keyboard=column)

def admin_battle_data_btns(link, com_id):
    column = []
    if link:
        column.append([InlineKeyboardButton(text="Go live 🎥", url=link)])
    column.append(
        [InlineKeyboardButton(text="Confirm ✅", callback_data=MyCallback(foo='confirm', bar=com_id).pack())])
    column.append(
        [InlineKeyboardButton(text="Cancel ❌", callback_data=MyCallback(foo='cancel', bar=com_id).pack())])
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=column)
