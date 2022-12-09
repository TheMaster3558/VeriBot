from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Final
    from ._types import Bot


__title__: Final[str] = 'veribot'
__author__: Final[str] = 'The Master'
__license__: Final[str] = 'MIT'
__copyright__: Final[str] = 'Copyright 2022-present The Master'
__version__: Final[str] = '2.0.0a'


from .cog import Verification


def _check_config(bot: Bot) -> None:
    if not hasattr(bot, 'config'):
        raise Exception('Bot missing attribute "config"')
    for key in ('veribot_channel_id', 'veribot_verified_role_id'):
        if key not in bot.config:
            raise Exception(f'Missing config key "{key}"')


def _check_intents(bot: Bot) -> None:
    if not bot.intents.members:
        raise Exception('veribot requires the members intent')


async def setup(bot: Bot) -> None:
    _check_config(bot)
    _check_intents(bot)
    await bot.add_cog(Verification(bot))


del TYPE_CHECKING
