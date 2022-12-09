from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import discord

from .utils import getch

if TYPE_CHECKING:
    from typing_extensions import Self
    from ._types import Bot
    from .database import Database


class ReasonModal(discord.ui.Modal, title='Rejection Reason'):
    reason = discord.ui.TextInput(label='reason', style=discord.TextStyle.short)

    interaction: discord.Interaction

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction


class VerificationView(discord.ui.View):
    def __init__(
        self, bot: Bot, db: Database, user: discord.abc.Snowflake, name: str
    ) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.db = db
        self.user = user
        self.name = name

    async def disable(
        self, message: discord.Message, approved: bool, reason: Optional[str] = None
    ) -> None:
        embed = message.embeds[0]
        if approved:
            embed.color = discord.Color.green()
        else:
            embed.color = discord.Color.red()

        if reason:
            # `is not None` not used to check for empty string too
            embed.add_field(name='Reason', value=reason)

        self.approve_button.disabled = True
        self.reject_button.disabled = True
        await message.edit(embed=embed, view=self, attachments=[])

        await self.db.remove_message(message)
        self.stop()

    @discord.ui.button(
        label='Approve', style=discord.ButtonStyle.green, custom_id='approve'
    )
    async def approve_button(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ) -> None:
        assert interaction.message is not None
        assert interaction.guild is not None

        await interaction.response.defer()

        try:
            member = await getch(interaction.guild.get_member, self.user.id)
        except discord.NotFound:
            await interaction.followup.send('The user has left this server.')
        else:
            await self.db.insert_user(member, self.name)
            await interaction.followup.send(f'{member} has been approved.')

            embed = discord.Embed(
                title='You have been verified',
                timestamp=discord.utils.utcnow(),
                color=discord.Color.green(),
            )
            await member.send(embed=embed)

            role = interaction.guild.get_role(
                self.bot.config['veribot_verified_role_id']
            )
            assert role is not None
            await member.add_roles(role)

        await self.disable(interaction.message, True)

    @discord.ui.button(
        label='Reject', style=discord.ButtonStyle.red, custom_id='reject'
    )
    async def reject_button(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ) -> None:
        assert interaction.message is not None
        assert interaction.guild is not None

        modal = ReasonModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        try:
            member = await getch(interaction.guild.get_member, self.user.id)
        except discord.NotFound:
            await modal.interaction.response.send_message(
                'The user has left the server.'
            )
        else:
            await modal.interaction.response.send_message(
                f'{member} has been rejected.', ephemeral=True
            )

            embed = discord.Embed(
                title='Your verification has been rejected',
                timestamp=discord.utils.utcnow(),
                color=discord.Color.red(),
            )
            embed.add_field(name='reason', value=modal.reason.value)
            await member.send(embed=embed)

        await self.disable(
            interaction.message, approved=False, reason=modal.reason.value
        )


async def add_views(bot: Bot, db: Database) -> None:
    await bot.wait_until_ready()
    channel = await getch(bot.get_channel, bot.config['veribot_channel_id'])
    assert isinstance(channel, discord.TextChannel)

    for message_id in await db.get_messages():
        message = await channel.fetch_message(message_id)
        embed = message.embeds[0]

        assert embed.title is not None and embed.footer.text is not None
        name = embed.title.strip('Name: ')
        user_id = embed.footer.text.strip('ID: ')
        view = VerificationView(bot, db, discord.Object(id=user_id), name)
        bot.add_view(view, message_id=message_id)
