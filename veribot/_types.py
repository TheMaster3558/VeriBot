from typing import Any, Dict

from discord.ext import commands


class Bot(commands.Bot):
    config: Dict[str, Any]
