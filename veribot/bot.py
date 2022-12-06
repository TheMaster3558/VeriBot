from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, TypeVar, Optional

import discord
from discord import app_commands
from discord.ext import commands

from .database import Database


R = TypeVar('R', bound=discord.abc.Snowflake)


class VeriBot(commands.Bot):
    app_commands_dict: Dict[str, app_commands.AppCommand]

    def __init__(
        self,
        *,
        intents: Optional[discord.Intents] = None,
        channel_id: int,
        guild_id: int,
        verified_role_id: int,
        **kwargs: Any,
    ) -> None:
        intents = intents or discord.Intents.default()
        intents.members = True

        super().__init__(
            command_prefix=commands.when_mentioned, intents=intents, **kwargs
        )

        self.channel_id: int = channel_id
        self.guild_id: int = guild_id
        self.verified_role_id: int = verified_role_id

        self.db: Database = Database()

    async def setup_hook(self) -> None:
        await self.db.init()

        await self.load_extension('commands')
        await self.load_extension('events')
        await self.load_extension('views')
        await self.load_extension('errors')
        await self.load_extension('jishaku')
        await self.load_extension('checks')

        test_guild = discord.Object(id=self.guild_id)
        self.app_commands_dict = {
            cmd.name: cmd for cmd in await self.tree.sync(guild=test_guild)
        }

    async def close(self) -> None:
        await self.db.close()

    @staticmethod
    async def getch(get: Callable[[int], Optional[R]], obj_id: int) -> R:
        fetch: Callable[[int], Awaitable[R]] = getattr(
            get.__self__, get.__name__.replace('get', 'fetch')
        )
        return get(obj_id) or await fetch(obj_id)
