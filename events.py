from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from constants import VERIFIED_ROLE_ID

if TYPE_CHECKING:
    from bot import Bot


async def setup(bot: Bot) -> None:
    @bot.listen()
    async def on_member_join(member: discord.Member) -> None:
        role = member.guild.get_role(VERIFIED_ROLE_ID)
        assert role is not None

        name = await bot.get_name(member)
        if name is not None:
            await member.add_roles(role)
        else:
            mention = bot.app_commands_dict['verify'].mention
            await member.send(f'Verify yourself with {mention}')
