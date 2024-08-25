from keyboards.inline.callback_data import MyCallback
from loader import dp, db, bot
from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.types.input_media_photo import InputMediaPhoto, InputMediaType
from datetime import datetime
from keyboards.inline.user_inline_btn import battle_data_link, battle_data
from utils.db_api.postgresql import Database
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

router = Router()
from scheduler import scheduler


# scheduler = db.scheduler()


def generate_caption(data):
    date_time_str = data['start_date']
    date_time_obj = datetime.fromisoformat(str(date_time_str))
    date = date_time_obj.date()
    time = date_time_obj.time().replace(tzinfo=None, microsecond=0)
    caption = f"<b>👊 {data['name']}</b>\n\n"
    caption += f"<i>📋 {data['description']}</i>\n\n"
    caption += f"<u>📅 Date: {date}</u>\n"
    caption += f"<u>🕔 Time: {time}</u>\n"
    return caption


# https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/magic_filters.html#magic-filters
# https://docs.aiogram.dev/en/dev-3.x/dispatcher/filters/callback_data.html
@dp.callback_query(MyCallback.filter(F.foo == 'back'))
async def selected_competition(query: CallbackQuery, callback_data: MyCallback):
    com = callback_data.unpack(query.data)
    sp_id = com.bar
    competitions = await db.select_competitions_by_sport_type_id(st_id=sp_id)
    image = await db.sport_type_image(id=sp_id)

    media = InputMediaPhoto(type=InputMediaType.PHOTO, media=image['file_id'],
                            caption="Quyidagi musobaqalardan birini tanlang")
    await query.message.edit_media(media=media, reply_markup=battle_data(competitions))


@dp.callback_query(MyCallback.filter(F.foo == 'cancel'))
async def competition_cancel(query: CallbackQuery, callback_data: MyCallback):
    print("bekor qilindi kirdi")

    com = callback_data.unpack(query.data)
    c_id = com.bar
    job = scheduler.get_job(c_id)
    if job:
        job.remove()
        await query.answer("Cancel ❌")
        await query.message.delete()
    else:
        await query.answer("Notification not found ❗️")
        await query.message.delete()


@dp.callback_query(MyCallback.filter(F.foo == 'confirm'))
async def competition_confirm(query: CallbackQuery, callback_data: MyCallback):
    com = callback_data.unpack(query.data)
    c_id = com.bar
    job = scheduler.get_job(c_id)
    if job:
        await query.answer("Confirm ✅")
        job.remove()
        competition = await db.find_by_id_competition(id=c_id)
        await query.message.delete()
        await db.send_notification_all(caption_arg=generate_caption(competition), competition=competition)
    else:
        await query.answer("Notification not found ❗️")





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
    sport_type_id = competition['sport_type_id']
    url = competition['stream_link']
    caption = generate_caption(competition)

    media = InputMediaPhoto(type=InputMediaType.PHOTO, media=competition['file_id'], caption=caption)
    await query.message.edit_media(media=media, reply_markup=battle_data_link(link=url, sport_type_id=sport_type_id))

