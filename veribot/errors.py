from __future__ import annotations

from typing import TYPE_CHECKING, List

import sys
import traceback

import discord

if TYPE_CHECKING:
    from ._types import Bot


async def get_owners(bot: Bot) -> List[discord.abc.Messageable]:
    assert bot.owner_ids is not None
    return [await bot.fetch_user(user_id) for user_id in bot.owner_ids]


async def report_error(bot: Bot, error: Exception) -> None:
    formatted = '\n'.join(
        traceback.format_exception(error.__class__, error, error.__traceback__)
    )
    print(formatted, file=sys.stdout)

    embed = discord.Embed(
        title='Error',
        description=f'```py\n{formatted}\n```',
        timestamp=discord.utils.utcnow(),
        color=discord.Color.red(),
    )

    for user in await get_owners(bot):
        await user.send(embed=embed)
