from __future__ import annotations

from typing import TYPE_CHECKING

import jishaku
import discord
from discord.ext import commands

if TYPE_CHECKING:
    from .bot import VeriBot


async def jsk_check(self: jishaku.Feature, ctx: commands.Context[VeriBot]) -> bool:
    if not await ctx.bot.is_owner(ctx.author) and (
        isinstance(ctx.author, discord.Member)
        and not ctx.author.guild_permissions.administrator
    ):
        raise commands.NotOwner('You must be a mod or owner to use jishaku.')
    return True


async def setup(bot: VeriBot) -> None:
    jishaku.Feature.cog_check = jsk_check  # type: ignore
