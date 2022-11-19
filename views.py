from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from constants import VERIFIED_ROLE_ID

if TYPE_CHECKING:
    from typing_extensions import Self
    from bot import Bot


def get_user_data(button: discord.ui.Button[VerificationView]) -> tuple[int, str]:
    assert button.custom_id is not None
    user_id, name = button.custom_id.split('_')
    return int(user_id), name


class ReasonModal(discord.ui.Modal, title='Rejection Reason'):
    reason = discord.ui.TextInput(label='reason', style=discord.TextStyle.short)

    interaction: discord.Interaction

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction


class VerificationView(discord.ui.View):
    def __init__(self, user: discord.abc.Snowflake, name: str) -> None:
        super().__init__(timeout=None)
        custom_id = f'{user.id}_{name}'
        self.approve_button.custom_id = custom_id
        self.reject_button.custom_id = custom_id

    async def disable(self, message: discord.Message, approved: bool) -> None:
        embed = message.embeds[0]
        if approved:
            embed.color = discord.Color.green()
        else:
            embed.color = discord.Color.red()

        self.approve_button.disabled = True
        self.reject_button.disabled = True
        await message.edit(embed=embed, view=self)

    @discord.ui.button(label='Approve', style=discord.ButtonStyle.green)
    async def approve_button(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ) -> None:
        assert interaction.message is not None
        assert interaction.guild is not None
        bot: Bot = interaction.client  # type: ignore

        await interaction.response.defer()

        user_id, name = get_user_data(button)
        try:
            member = await bot.getch(interaction.guild.fetch_member, user_id)
        except discord.NotFound:
            await interaction.followup.send('The user has left this server.')
        else:
            await bot.insert_user(member, name)
            await interaction.response.send_message(f'{member} has been approved.')

            embed = discord.Embed(
                title='You have been verified',
                timestamp=discord.utils.utcnow(),
                color=discord.Color.green(),
            )
            await member.send(embed=embed)

            role = interaction.guild.get_role(VERIFIED_ROLE_ID)
            assert role is not None
            await member.add_roles(role)

        await self.disable(interaction.message, True)

    @discord.ui.button(label='Reject', style=discord.ButtonStyle.red)
    async def reject_button(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ) -> None:
        assert interaction.message is not None
        assert interaction.guild is not None
        bot: Bot = interaction.client  # type: ignore

        modal = ReasonModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        user_id, _ = get_user_data(button)
        try:
            member = await bot.getch(interaction.guild.fetch_member, user_id)
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

        await self.disable(interaction.message, False)
