from typing import Awaitable, Callable, Dict, TypeVar, Optional

import discord
from discord import app_commands
from discord.ext import commands

from constants import GUILD_ID
from database import Database


R = TypeVar('R', bound=discord.abc.Snowflake)


class Bot(Database, commands.Bot):
    app_commands_dict: Dict[str, app_commands.AppCommand]
    test_guild = discord.Object(id=GUILD_ID)

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            owner_ids={475315771086602241, 739510612652195850},
        )

    async def setup_hook(self) -> None:
        await super().setup_hook()
        await self.load_extension('commands')
        await self.load_extension('events')
        await self.load_extension('views')
        await self.load_extension('errors')
        await self.load_extension('jishaku')
        await self.load_extension('checks')

        self.app_commands = {
            cmd.name: cmd for cmd in await self.tree.sync(guild=self.test_guild)
        }

    async def getch(self, get: Callable[[int], Optional[R]], obj_id: int) -> R:
        fetch: Callable[[int], Awaitable[R]] = getattr(
            get.__self__, get.__name__.replace('get', 'fetch')
        )
        return get(obj_id) or await fetch(obj_id)
