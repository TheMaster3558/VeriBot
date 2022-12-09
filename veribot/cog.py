from __future__ import annotations

import io
from typing import TYPE_CHECKING

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

from .database import Database
from .errors import report_error
from .utils import fetch_app_command_mention, getch
from .views import add_views, VerificationView

if TYPE_CHECKING:
    from ._types import Bot


class Verification(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = Database()

    async def cog_load(self) -> None:
        await self.db.init()
        self.bot.loop.create_task(add_views(self.bot, self.db))

    async def cog_unload(self) -> None:
        await self.db.close()

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        await interaction.response.send_message(
            'An unexpected error occurred.', ephemeral=True
        )
        await report_error(self.bot, error)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        role = member.guild.get_role(self.bot.config['veribot_role_id'])
        assert role is not None

        name = await self.db.get_name(member)
        if name is not None:
            await member.add_roles(role)
        else:
            mention = await fetch_app_command_mention(self.bot, member.guild, 'verify')
            await member.send(f'Verify yourself with {mention}.')

    @app_commands.command(name='verify', description='Verify yourself')
    @app_commands.describe(
        name='Your name', image='A photo to help you with verification'
    )
    async def verify_command(
        self, interaction: discord.Interaction, name: str, image: discord.Attachment
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title=f'Name: {name}', timestamp=discord.utils.utcnow(), color=0x2F3136
        )
        embed.set_author(
            name=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )
        embed.set_image(url=f'attachment://{image.filename}')
        embed.set_footer(text=f'ID: {interaction.user.id}')

        view = VerificationView(self.bot, self.db, interaction.user, name)

        channel = await getch(
            self.bot.get_channel, self.bot.config['veribot_channel_id']
        )
        assert isinstance(channel, discord.TextChannel)

        data = await image.read()
        buffer = io.BytesIO(data)
        file = discord.File(buffer, image.filename)

        message = await channel.send(embed=embed, file=file, view=view)
        await self.db.insert_message(message)
        await interaction.followup.send('Your verification has been sent.')

    @app_commands.command(
        name='whois', description='Get the name a user used for verification'
    )
    @app_commands.describe(user='The user to check')
    @app_commands.default_permissions(administrator=True)
    async def whois_command(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        name = await self.db.get_name(user)
        if name is None:
            mention = await fetch_app_command_mention(
                self.bot, interaction.guild, 'rename'
            )
            await interaction.followup.send(
                f'That user could not be found. Use {mention} to add them.',
                ephemeral=True,
            )
        else:
            await interaction.followup.send(name, ephemeral=True)

    @app_commands.command(name='rename', description='Rename a user for verification')
    @app_commands.describe(
        user='The user to rename', new_name='The new name for the user'
    )
    @app_commands.default_permissions(administrator=True)
    async def rename_command(
        self, interaction: discord.Interaction, user: discord.Member, new_name: str
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            await self.db.remove_user(user)
        except aiosqlite.OperationalError:
            pass
        await self.db.insert_user(user, new_name)
        await interaction.followup.send(
            f'{user}\'s new name is {new_name}.', ephemeral=True
        )

    @app_commands.command(name='unverify', description='Unverify a user')
    @app_commands.describe(user='The user to unverify')
    @app_commands.default_permissions(administrator=True)
    async def unverify_command(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        assert interaction.guild is not None

        await interaction.response.defer(ephemeral=True)
        try:
            await self.db.remove_user(user)
        except aiosqlite.OperationalError:
            await interaction.followup.send(
                'That user was never verified.', ephemeral=True
            )
        else:
            await interaction.followup.send(
                f'The {user} was unverified.', ephemeral=True
            )

        role = interaction.guild.get_role(self.bot.config['veribot_verified_role_id'])
        assert role is not None

        if role in user.roles:
            await user.remove_roles(role)
