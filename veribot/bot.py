from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, TypeVar, Optional

import discord
from discord import app_commands
from discord.ext import commands

from .database import Database

if TYPE_CHECKING:
    import datetime


R = TypeVar('R', bound=discord.abc.Snowflake)


class VeriBot(commands.Bot):
    app_commands_dict: Dict[str, app_commands.AppCommand]
    startup_time: datetime.datetime

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

        await self.load_extension('veribot.commands')
        await self.load_extension('veribot.events')
        await self.load_extension('veribot.last_sync')
        await self.load_extension('veribot.views')
        await self.load_extension('veribot.errors')
        await self.load_extension('veribot.checks')
        await self.load_extension('jishaku')

        self.startup_time = discord.utils.utcnow()

    async def close(self) -> None:
        await self.db.close()

    @staticmethod
    async def getch(get: Callable[[int], Optional[R]], obj_id: int) -> R:
        fetch: Callable[[int], Awaitable[R]] = getattr(
            get.__self__, get.__name__.replace('get', 'fetch')
        )
        return get(obj_id) or await fetch(obj_id)
