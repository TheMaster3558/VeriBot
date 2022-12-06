from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from .bot import VeriBot


async def setup(bot: VeriBot) -> None:
    @bot.listen()
    async def on_member_join(member: discord.Member) -> None:
        role = member.guild.get_role(bot.verified_role_id)
        assert role is not None

        name = await bot.db.get_name(member)
        if name is not None:
            await member.add_roles(role)
        else:
            mention = bot.app_commands_dict['verify'].mention
            await member.send(f'Verify yourself with {mention}')
