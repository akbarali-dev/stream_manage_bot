from aiogram import types
from aiogram import Bot


async def set_default_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="🔄 Launch the bot"),
        # types.BotCommand(command="/help", description="Help"),
        # types.BotCommand(command="/menu", description="Menu")
    ]
    await bot.set_my_commands(commands=commands)
