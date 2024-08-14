from keyboards.inline.callback_data import MyCallback
from loader import dp, db
from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.types.input_media_photo import InputMediaPhoto, InputMediaType
from datetime import datetime
from keyboards.inline.user_inline_btn import battle_data_link, battle_data

router = Router()


# https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/magic_filters.html#magic-filters
# https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/callback_data.html
@dp.callback_query(MyCallback.filter(F.foo == 'back'))
async def selected_competition(query: CallbackQuery, callback_data: MyCallback):
    com = callback_data.unpack(query.data)
    sp_id = com.bar
    competitions = await db.select_competitions_by_sport_type_id(st_id=sp_id)
    image = await db.sport_type_image(id=sp_id)

    media = InputMediaPhoto(type=InputMediaType.PHOTO, media=image['file_id'], caption="Quyidagi musobaqalardan birini tanlang")
    await query.message.edit_media(media=media, reply_markup=battle_data(competitions))


@dp.callback_query(MyCallback.filter(F.foo == 'select_competition'))
async def selected_competition(query: CallbackQuery, callback_data: MyCallback):
    com = callback_data.unpack(query.data)
    competition_id = com.bar
    competition = await db.find_by_id_competition(id=competition_id)
    if not competition:
        await query.message.answer("Xech narsa topilmadi")
        return
    if not competition['active']:
        await query.message.answer("Xech narsa topilmadi")
        return
    date_time_str = competition['start_date']
    sport_type_id = competition['sport_type_id']
    url = competition['stream_link']
    date_time_obj = datetime.fromisoformat(str(date_time_str))
    date = date_time_obj.date()
    time = date_time_obj.time().replace(tzinfo=None, microsecond=0)
    caption = f"<b>👊 {competition['name']}</b>\n\n"
    caption += f"<i>📋 {competition['description']}</i>\n\n"
    caption += f"<u>📅 Kun: {date}</u>\n"
    caption += f"<u>🕔 Vaqti: {time}</u>\n"

    media = InputMediaPhoto(type=InputMediaType.PHOTO, media=competition['file_id'], caption=caption)
    await query.message.edit_media(media=media, reply_markup=battle_data_link(link=url, sport_type_id=sport_type_id))
