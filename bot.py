from typing import Awaitable, Callable, Dict, TypeVar

import discord
from discord import app_commands
from discord.ext import commands

from constants import GUILD_ID, TOKEN
from database import Database


R = TypeVar('R', bound=discord.abc.Snowflake)


class Bot(Database, commands.Bot):
    app_commands_dict: Dict[str, app_commands.AppCommand]
    test_guild = discord.Object(id=GUILD_ID)

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix='sb!', intents=intents)

    def standard_run(self) -> None:
        self.run(TOKEN)

    async def setup_hook(self) -> None:
        await super().setup_hook()
        self.app_commands = {
            cmd.name: cmd for cmd in await self.tree.sync(guild=self.test_guild)
        }

    async def getch(self, fetch: Callable[[int], Awaitable[R]], obj_id: int) -> R:
        get = getattr(fetch.__self__, fetch.__name__.replace('fetch', 'get'))
        return get(obj_id) or await fetch(obj_id)
