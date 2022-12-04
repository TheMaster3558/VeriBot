from __future__ import annotations

from typing import TYPE_CHECKING, List

import sys
import traceback

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from .bot import VeriBot


async def get_owners(bot: VeriBot) -> List[discord.abc.Messageable]:
    assert bot.owner_ids is not None
    return [await bot.fetch_user(user_id) for user_id in bot.owner_ids]


async def report_error(bot: VeriBot, error: Exception) -> None:
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


async def interactions_error_handler(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    bot: VeriBot = interaction.client  # type: ignore
    assert bot.application is not None

    await report_error(bot, error)


async def commands_error_handler(
    ctx: commands.Context[VeriBot], error: commands.CommandError
) -> None:
    if isinstance(error, commands.NotOwner):
        await ctx.send(error.args[0])
    else:
        await report_error(ctx.bot, error)


async def setup(bot: VeriBot) -> None:
    bot.tree.error(interactions_error_handler)
    bot.add_listener(commands_error_handler, 'on_command_error')
