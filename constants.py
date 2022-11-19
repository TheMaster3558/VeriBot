from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from typing_extensions import TypedDict

    class ConfigData(TypedDict):
        channel_id: int
        guild_id: int
        verified_role_id: int
        token: str


with open('config.json') as f:
    data: ConfigData = json.load(f)

CHANNEL_ID: Final[int] = data['channel_id']
GUILD_ID: Final[int] = data['guild_id']
VERIFIED_ROLE_ID: Final[int] = data['verified_role_id']
TOKEN: Final[str] = data['token']
