from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, MenuButton


def question_btn(sport_names):
    column = list()
    row = list()
    for i in range(0, len(sport_names)):
        row.append(KeyboardButton(text=sport_names[i]['name']))
        if i % 2 == 1:
            column.append(row)
            row = []
    row.append(KeyboardButton(text="🏠Asosiy menu"))
    column.append(row)
    sport_btns = ReplyKeyboardMarkup(keyboard=column, resize_keyboard=True)
    return sport_btns

