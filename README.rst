VeriBot
=======
VeriBot is a cog that can be used for verification. This is important in servers such as school servers
where you need to know who everyone is.


Installation
------------
To install the stable version, you can run the following command

.. code:: sh

    # Linux/macOS
    python3 -m pip install veribot

    # Windows
    py -3 -m pip install veribot


To install the development version, you can run the following command

.. code:: sh

    # Linux/macOS
    python3 -m pip install git+https://github.com/TheMaster3558/veribot

    # Windows
    py -3 -m pip install git+https://github.com/TheMaster3558/veribot


How does the bot work?
----------------------
When a user joins the server they are prompted to use the `/verify` command.
When a user runs `/verify`, their name and any image they provided will be sent to the set channel.
From their moderators have the option to accept or reject the user.

After approval, moderators can view who a user is, rename the user, or unverify the user.


Config
------
The bot must have an attribute ``config`` which is a dictionary with the keys of ``veribot_channel_id`` and ``veribot_verified_role_id``.


App Commands
------------
The cog adds the app commands but does not sync them. **You** are responsible for syncing.


Example
-------
.. code:: py

    import asyncio
    import discord
    from discord.ext import commands


    intents = discord.Intents.default()
    intents.members = True

    bot = commands.Bot(command_prefix=[], intents=intents)
    bot.config = {'veribot_channel_id': 0, 'veribot_verified_role_id': 0}
    # `veribot_channel_id` is the channel to accept/reject from
    # `veribot_verified_role_id` is the role to add the a user if they get approved

    async def main():
        async with bot:
            await bot.load_extension('veribot')
            await bot.start('token')


    asyncio.run(main())
