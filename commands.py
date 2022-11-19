from __future__ import annotations

from typing import TYPE_CHECKING

import aiosqlite
import discord
from discord import app_commands

from constants import CHANNEL_ID, VERIFIED_ROLE_ID

if TYPE_CHECKING:
    from bot import Bot


@app_commands.command(name='verify', description='Verify yourself')
@app_commands.describe(name='Your name', image='A photo to help you with verification')
async def verify_command(
    interaction: discord.Interaction, name: str, image: discord.File
) -> None:
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(title=f'Name: {name}', timestamp=discord.utils.utcnow(), color=0x2F3136)
    embed.set_author(
        name=str(interaction.user), icon_url=interaction.user.display_avatar.url
    )
    embed.set_image(url=f'attachment://{image.filename}')

    channel = interaction.client.get_channel(
        CHANNEL_ID
    ) or await interaction.client.fetch_channel(CHANNEL_ID)
    assert isinstance(channel, discord.TextChannel)

    await channel.send(embed=embed, file=image)
    await interaction.followup.send('Your verification has been sent.')


@app_commands.command(
    name='whois', description='Get the name a user used for verification'
)
@app_commands.describe(user='The user to check')
@app_commands.default_permissions(administrator=True)
async def whois_command(interaction: discord.Interaction, user: discord.Member) -> None:
    bot: Bot = interaction.client  # type: ignore

    await interaction.response.defer(ephemeral=True)
    name = await bot.get_name(user)
    if name is None:
        await interaction.followup.send('That user could not be found.', ephemeral=True)
    else:
        await interaction.followup.send(name, ephemeral=True)


@app_commands.command(name='rename', description='Rename a user for verification')
@app_commands.describe(user='The user to rename', new_name='The new name for the user')
@app_commands.default_permissions(administrator=True)
async def rename_command(
    interaction: discord.Interaction, user: discord.Member, new_name: str
) -> None:
    bot: Bot = interaction.client  # type: ignore

    await interaction.response.defer(ephemeral=True)
    try:
        await bot.remove_user(user)
    except aiosqlite.OperationalError:
        pass
    await bot.insert_user(user, new_name)
    await interaction.followup.send(
        f'{user}\'s new name is {new_name}.', ephemeral=True
    )


@app_commands.command(name='unverify', description='Unverify a user')
@app_commands.default_permissions(administrator=True)
async def unverify_command(
    interaction: discord.Interaction, user: discord.Member
) -> None:
    assert interaction.guild is not None
    bot: Bot = interaction.client  # type: ignore

    await interaction.response.defer(ephemeral=True)
    try:
        await bot.remove_user(user)
    except aiosqlite.OperationalError:
        await interaction.followup.send('That user was never verified.', ephemeral=True)
    else:
        await interaction.followup.send('The user was unverified.', ephemeral=True)

    role = interaction.guild.get_role(VERIFIED_ROLE_ID)
    assert role is not None

    if role in user.roles:
        await user.remove_roles(role)
