from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, TypeVar, Optional

import discord
from discord import app_commands
from discord.ext import commands

from .database import Database


if TYPE_CHECKING:
    from typing_extensions import TypedDict

    class ConfigData(TypedDict):
        channel_id: int
        guild_id: int
        verified_role_id: int


R = TypeVar('R', bound=discord.abc.Snowflake)


class VeriBot(commands.Bot):
    app_commands_dict: Dict[str, app_commands.AppCommand]

    def __init__(
        self, *, channel_id: int, guild_id: int, verified_role_id: int, **kwargs: Any
    ) -> None:
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            command_prefix=commands.when_mentioned, intents=intents, **kwargs
        )

        self.config: ConfigData = {
            'channel_id': channel_id,
            'guild_id': guild_id,
            'verified_role_id': verified_role_id,
        }
        self.db: Database = Database()

    async def setup_hook(self) -> None:
        await self.load_extension('commands')
        await self.load_extension('events')
        await self.load_extension('views')
        await self.load_extension('errors')
        await self.load_extension('jishaku')
        await self.load_extension('checks')

        test_guild = discord.Object(id=self.config['guild_id'])
        self.app_commands_dict = {
            cmd.name: cmd for cmd in await self.tree.sync(guild=test_guild)
        }

    @staticmethod
    async def getch(get: Callable[[int], Optional[R]], obj_id: int) -> R:
        fetch: Callable[[int], Awaitable[R]] = getattr(
            get.__self__, get.__name__.replace('get', 'fetch')
        )
        return get(obj_id) or await fetch(obj_id)
