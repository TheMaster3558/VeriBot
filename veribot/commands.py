from __future__ import annotations

import io
from typing import TYPE_CHECKING

import aiosqlite
import discord
from discord import app_commands

from . import __author__
from .views import VerificationView

if TYPE_CHECKING:
    from .bot import VeriBot


@app_commands.command(name='verify', description='Verify yourself')
@app_commands.describe(name='Your name', image='A photo to help you with verification')
async def verify_command(
    interaction: discord.Interaction, name: str, image: discord.Attachment
) -> None:
    bot: VeriBot = interaction.client  # type: ignore

    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title=f'Name: {name}', timestamp=discord.utils.utcnow(), color=0x2F3136
    )
    embed.set_author(
        name=str(interaction.user), icon_url=interaction.user.display_avatar.url
    )
    embed.set_image(url=f'attachment://{image.filename}')
    embed.set_footer(text=f'ID: {interaction.user.id}')

    view = VerificationView(bot, interaction.user, name)

    channel = await bot.getch(bot.get_channel, bot.channel_id)
    assert isinstance(channel, discord.TextChannel)

    data = await image.read()
    buffer = io.BytesIO(data)
    file = discord.File(buffer, image.filename)

    message = await channel.send(embed=embed, file=file, view=view)
    await bot.db.insert_message(message)
    await interaction.followup.send('Your verification has been sent.')


@app_commands.command(
    name='whois', description='Get the name a user used for verification'
)
@app_commands.describe(user='The user to check')
@app_commands.default_permissions(administrator=True)
async def whois_command(interaction: discord.Interaction, user: discord.Member) -> None:
    bot: VeriBot = interaction.client  # type: ignore

    await interaction.response.defer(ephemeral=True)
    name = await bot.db.get_name(user)
    if name is None:
        mention = bot.app_commands_dict['rename'].mention
        await interaction.followup.send(
            f'That user could not be found. Use {mention} to add them.', ephemeral=True
        )
    else:
        await interaction.followup.send(name, ephemeral=True)


@app_commands.command(name='rename', description='Rename a user for verification')
@app_commands.describe(user='The user to rename', new_name='The new name for the user')
@app_commands.default_permissions(administrator=True)
async def rename_command(
    interaction: discord.Interaction, user: discord.Member, new_name: str
) -> None:
    bot: VeriBot = interaction.client  # type: ignore

    await interaction.response.defer(ephemeral=True)
    try:
        await bot.db.remove_user(user)
    except aiosqlite.OperationalError:
        pass
    await bot.db.insert_user(user, new_name)
    await interaction.followup.send(
        f'{user}\'s new name is {new_name}.', ephemeral=True
    )


@app_commands.command(name='unverify', description='Unverify a user')
@app_commands.describe(user='The user to unverify')
@app_commands.default_permissions(administrator=True)
async def unverify_command(
    interaction: discord.Interaction, user: discord.Member
) -> None:
    assert interaction.guild is not None
    bot: VeriBot = interaction.client  # type: ignore

    await interaction.response.defer(ephemeral=True)
    try:
        await bot.db.remove_user(user)
    except aiosqlite.OperationalError:
        await interaction.followup.send('That user was never verified.', ephemeral=True)
    else:
        await interaction.followup.send(f'The {user} was unverified.', ephemeral=True)

    role = interaction.guild.get_role(bot.verified_role_id)
    assert role is not None

    if role in user.roles:
        await user.remove_roles(role)


@app_commands.command(name='info', description='Info about the bot')
async def info_command(interaction: discord.Interaction) -> None:
    embed = discord.Embed(
        title=interaction.client.user.name,
        description=f'{interaction.client.user} is an instance of [VeriBot](https://github.com/TheMaster3558/VeriBot). VeriBot is an open source verification bot created by {__author__}.',
    )
    embed.add_field(
        name='Bot Created',
        value=discord.utils.format_dt(interaction.client.user.created_at, style='R'),
    )
    embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


async def setup(bot: VeriBot) -> None:
    for obj in globals().values():
        if isinstance(obj, app_commands.Command):
            bot.tree.add_command(obj)
