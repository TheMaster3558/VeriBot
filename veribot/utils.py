from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Awaitable, Callable, Optional, TypeVar

import discord

if TYPE_CHECKING:
    from ._types import Bot


R = TypeVar('R', bound=discord.abc.Snowflake)


@functools.lru_cache()
async def fetch_app_command_mention(
    bot: Bot, guild: discord.Guild, command_name: str
) -> str:
    test_guild = discord.Object(id=guild.id)
    all_app_commands = await bot.tree.fetch_commands() or await bot.tree.fetch_commands(
        guild=test_guild
    )
    for command in all_app_commands:
        if command.name == command_name:
            return command.mention
    return f'/{command_name}'


async def getch(get: Callable[[int], Optional[R]], obj_id: int) -> R:
    fetch: Callable[[int], Awaitable[R]] = getattr(
        get.__self__, get.__name__.replace('get', 'fetch')
    )
    return get(obj_id) or await fetch(obj_id)
