from typing import Union
import asyncio
import asyncpg

from asyncpg.pool import Pool
from asyncpg import Connection
from data import config
# from loader import bot
import importlib
import json


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=5432
        )

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

    @staticmethod
    def notification_handler(connection, pid, channel, payload):
        """Notification kelganda ishlovchi funksiya"""

        data = json.loads(payload)
        message = data.get('payload')
        send_bot = data.get('send_bot')
        send_channel = data.get('send_channel')
        description = data.get('description')
        file_id = data.get('file_id')
        print(f"Olingan xabar: Channel={channel}, Payload={payload}")
        module_a = importlib.import_module('loader')

        # asyncio.create_task(module_a.bot.send_message(chat_id='1474104201', text=description))
        asyncio.create_task(
            module_a.bot.send_photo(chat_id='1474104201', photo=file_id, caption=description, parse_mode="HTML"))

    # async def select_user_info(self, **kwargs):
    #     sql = """
    #     select *
    #     from bot_api_botuser
    #     where
    #     """
    #     sql, parameters = self.format_args(sql, kwargs)
    #     return await self.execute(sql, *parameters, fetchrow=True)

    async def sport_types(self, **kwargs):
        sql = """
        select name
        from sport_types
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
        pass

    async def select_competitions_by_sport_type(self, name, **kwargs):
        sql = f"""
        select c.name, c.id::text
        from competition c
        join sport_types st on c.sport_type_id = st.id
        where st.name = '{name}' and c.active = true
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
