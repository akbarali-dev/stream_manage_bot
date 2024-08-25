from datetime import datetime, timedelta
from typing import Union
import asyncio
import asyncpg

from asyncpg.pool import Pool
from asyncpg import Connection
from data import config
# from loader import bot
import importlib
import json
from keyboards.inline.user_inline_btn import admin_battle_data_btns, stream_link
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler import scheduler
from apscheduler.schedulers import SchedulerAlreadyRunningError


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None
        self.is_confirmed = True

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=5432
        )

    def cancel(self):
        self.is_confirmed = False

    def confirm(self):
        self.is_confirmed = True

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def listen(self, channel: str):
        """Notificationlarni tinglash"""
        async with self.pool.acquire() as connection:
            connection: Connection
            await connection.add_listener(channel, self.notification_handler)

            print(f"Tinglashni boshladim '{channel}' kanalida...")
            while True:
                await asyncio.sleep(10)

    async def notification_handler(self, connection, pid, channel, payload):
        """Notification kelganda ishlovchi funksiya"""
        data = json.loads(payload)
        # asyncio.create_task(self.send_admin(data))
        msgs_ids = await self.send_admin(data)
        run_at = datetime.now() + timedelta(seconds=30)
        scheduler.add_job(func=self.send_notification_all,
                          trigger=IntervalTrigger(start_date=run_at, end_date=run_at + timedelta(seconds=0.1)),
                          id=data.get('id'),
                          kwargs={"data": data, "msgs": msgs_ids})
        try:
            scheduler.start()
        except SchedulerAlreadyRunningError:
            pass
        print("Vazifa qo'shildi!")

    def send_all_user(self, data):
        asyncio.create_task(self.send_notification_all(data))

    async def send_admin(self, data):
        send_msgs = {}
        module_a = importlib.import_module('loader')
        admins = await self.select_admins()
        for admin in admins:
            msg = await module_a.bot.send_photo(chat_id=admin['chat_id'],
                                          caption=self.generate_caption(data),
                                          photo=data.get('file_id'),
                                          reply_markup=admin_battle_data_btns(data.get('stream_link'),
                                                                              data.get('id')))
            send_msgs[msg.chat.id] = msg.message_id
        return send_msgs

    def generate_caption(self, data):
        date_time_str = data.get('start_date')
        date_time_obj = datetime.fromisoformat(str(date_time_str))
        date = date_time_obj.date()
        time = date_time_obj.time().replace(tzinfo=None, microsecond=0)
        caption = f"<b>👊 {data.get('name')}</b>\n\n"
        caption += f"<i>📋 {data.get('description')}</i>\n\n"
        caption += f"<u>📅 Date: {date}</u>\n"
        caption += f"<u>🕔 Time: {time}</u>\n"
        return str(caption)

    async def send_notification(self, chat_id, caption, file_id, markup, loader):
        try:
            await loader.bot.send_photo(chat_id=chat_id,
                                        caption=caption,
                                        photo=file_id, reply_markup=markup)
        except Exception as e:
            print(e)

    async def send_notification_all(self, data=None, competition=None, caption_arg=None, msgs = None):
        caption=""
        link=""
        file_id=""
        send_bot=False
        send_channel=False
        loader = importlib.import_module('loader')
        com_id = ""
        if data:
            caption = self.generate_caption(data)
            link = data.get('stream_link')
            file_id = data.get('file_id')
            send_bot = data.get('send_bot')
            send_channel = data.get('send_channel')
            com_id = data.get('id')

        elif competition:
            caption = caption_arg
            link = competition['stream_link']
            file_id = competition['file_id']
            send_bot = competition['send_bot']
            send_channel = competition['send_channel']
            com_id = competition['id']
        if msgs:
            for c_id, m_id in msgs.items():
                await loader.bot.delete_message(chat_id=c_id, message_id=m_id)

        markup = stream_link(link)
        if send_bot:
            async for user_ids in self.fetch_all_user_ids_in_batches(batch_size=1000):
                tasks = [
                    self.send_notification(user_id['chat_id'], caption, file_id, markup, loader)
                    for user_id in user_ids
                ]
                await asyncio.gather(*tasks)
                await asyncio.sleep(1)
        if send_channel:
            channels =await self.select_channel(com_id=com_id)
            for channel in channels:
                await self.send_notification("@"+channel['username'], caption, file_id, markup, loader)
                await asyncio.sleep(1)


    async def fetch_all_user_ids_in_batches(self, batch_size: int = 1000):
        offset = 0
        while True:
            user_ids = await self.select_users_pagination(limit=batch_size, offset=offset)
            if not user_ids:
                break
            yield user_ids
            offset += batch_size

    async def test(self):
        await asyncio.sleep(2)
        admins = await self.select_admins()
        return admins

    async def select_admins(self, **kwargs):
        sql = """
                select chat_id
                from users where is_admin=true
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_users(self, **kwargs):
        sql = """
                select chat_id
                from users 
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    async def select_channel_list(self, com_id):
        return await self.select_channel(com_id)
    async def select_channel(self, com_id,**kwargs):
        sql = """
            select c.username
            from competition com
            join competition_channels cc on com.id = cc.competition_id
            join channels c on c.id = cc.channel_id
            where com.id = $1
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql,com_id, *parameters, fetch=True)

    async def select_all_channel(self, **kwargs):
        sql = """
            select name, username
            from channels
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_users_pagination(self, limit, offset):
        sql = """
            select chat_id
            from users
            order by created_at
            limit $1 offset $2
            """
        return await self.execute(sql, limit, offset, fetch=True)

    async def sport_types(self, **kwargs):
        sql = """
                select distinct st.name
                from competition c
                    join sport_types st on c.sport_type_id = st.id
                where c.active = true
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def sport_type_image(self, **kwargs):
        sql = """
            select file_id
            from sport_types
            where 
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def competition(self, **kwargs):
        sql = """
            select *
            from competition
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def find_by_id_competition(self, **kwargs):
        sql = """
                select id, name, description, start_date, stream_link, file_id, active, sport_type_id::text, send_bot, send_channel
                from competition where 
    
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def already_exists_sport_type(self, name, **kwargs):
        sql = f"""
            SELECT
                CASE
                    WHEN EXISTS (SELECT 1 FROM sport_types WHERE name = '{name}')
                    THEN true
                    ELSE false
                END as result
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def already_exists_user(self, chat_id, **kwargs):
        sql = f"""
            SELECT CASE
               WHEN EXISTS (SELECT 1 FROM users WHERE chat_id = '{chat_id}')
                   THEN true
               ELSE false
               END as result;
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def add_user(self, full_name, chat_id):
        sql = ("INSERT INTO users (created_at, updated_at, is_admin, full_name, active, chat_id) "
               "VALUES(NOW(), NOW(),false, $1,$2, $3) returning *")
        return await self.execute(sql, full_name, True, str(chat_id), fetchrow=True)

    async def select_competitions_by_sport_type(self, name, **kwargs):
        sql = f"""
            select c.name, c.id::text
            from competition c
            join sport_types st on c.sport_type_id = st.id
            where st.name = '{name}' and c.active = true
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_competitions_by_sport_type_id(self, st_id, **kwargs):
        sql = f"""
            select c.name, c.id::text
            from competition c
            join sport_types st on c.sport_type_id = st.id
            where st.id = '{st_id}' and c.active = true
            """
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    #
    # async def select_answer(self, **kwargs):
    #     sql = """
    #     select answer
    #     from bot_api_answerquestions
    #     where
    #     """
    #     sql, parameters = self.format_args(sql, kwargs)
    #     return await self.execute(sql, *parameters, fetchrow=True)
    #
    # async def select_file(self, **kwargs):
    #     sql = """
    #     select file_link
    #     from bot_api_file
    #     where
    #     """
    #     sql, parameters = self.format_args(sql, kwargs)
    #     return await self.execute(sql, *parameters, fetch=True)
    #
    # async def select_contacts(self, **kwargs):
    #     sql = """
    #     select name, link
    #     from bot_api_contact
    #     where
    #     """
    #     sql, parameters = self.format_args(sql, kwargs)
    #     return await self.execute(sql, *parameters, fetch=True)
    #
    # async def select_portfolio(self, **kwargs):
    #     sql = """
    #     select id, title
    #     from bot_api_portfolio
    #     where
    #     """
    #     sql, parameters = self.format_args(sql, kwargs)
    #     return await self.execute(sql, *parameters, fetch=True)
    #
    # async def select_portfolio_by_id(self, **kwargs):
    #     sql = """
    #     select id, title, description, link
    #     from bot_api_portfolio
    #     where
    #     """
    #     sql, parameters = self.format_args(sql, kwargs)
    #     return await self.execute(sql, *parameters, fetchrow=True)
