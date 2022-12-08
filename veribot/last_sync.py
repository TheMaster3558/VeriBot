from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, List

import aiofiles
import discord

if TYPE_CHECKING:
    from .bot import VeriBot


# the keys of the json file are the id of the bot user
# this makes separate bots separate from each other


async def init_file() -> None:
    async with aiofiles.open('veribot/last_sync.json', 'w') as file:
        await file.write('{}')


async def read_file(bot: VeriBot) -> List[Dict[str, Any]]:
    async with aiofiles.open('veribot/last_sync.json', 'r') as file:
        text = await file.read()

    try:
        data: Dict[str, List[Dict[str, Any]]] = json.loads(text)
    except json.JSONDecodeError:
        await init_file()
        return await read_file(bot)
    return data.get(str(bot.user.id), [])


async def write_file(bot: VeriBot) -> None:
    async with aiofiles.open('veribot/last_sync.json', 'r') as file:
        text = await file.read()

    try:
        data: Dict[str, List[Dict[str, Any]]] = json.loads(text)
    except json.JSONDecodeError:
        await init_file()
        await write_file(bot)
    else:
        test_guild = discord.Object(id=bot.guild_id)
        data[str(bot.user.id)] = [command.to_dict() for command in bot.tree.get_commands(guild=test_guild)]
        dumped = json.dumps(data)

        async with aiofiles.open('veribot/last_sync.json', 'w') as file:
            await file.write(dumped)


async def should_write(bot: VeriBot) -> bool:
    test_guild = discord.Object(id=bot.guild_id)
    return await read_file(bot) != [command.to_dict() for command in bot.tree.get_commands(guild=test_guild)]


async def setup(bot: VeriBot) -> None:
    test_guild = discord.Object(id=bot.guild_id)
    bot.tree.copy_global_to(guild=test_guild)
    if await should_write(bot):
        bot.app_commands_dict = {
            cmd.name: cmd for cmd in await bot.tree.sync(guild=test_guild)
        }
        await write_file(bot)
