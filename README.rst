VeriBot
=======
VeriBot is a bot that can be used for verification. This is important in servers such as school servers
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


Example
-------
.. code:: py

    import veribot

    bot = veribot.VeriBot(
        channel_id=881609972469866527,  # this is the channel you can accept/reject from,
        guild_id=878431847162466354,  # the id of the server the bot is being used in
        verified_role_id=879147463020281907,  # the id of the role to add to users that have been verified

    bot.run('token')


Final Note
----------
It is recommended to be familiar with discord.py before using this bot.

