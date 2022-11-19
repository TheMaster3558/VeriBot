from typing import Optional

import aiosqlite
import discord


class Database:
    conn: aiosqlite.Connection

    async def setup_hook(self) -> None:
        self.conn = await aiosqlite.connect('verification.db')

    async def close(self) -> None:
        await self.conn.close()

    async def init(self) -> None:
        await self.conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (user_id int, name text)
            '''
        )

    async def insert_user(self, user: discord.abc.Snowflake, name: str) -> None:
        await self.conn.execute(
            '''
            INSERT INTO users VALUES (?, ?)
            ''',
            (user.id, name),
        )

    async def remove_user(self, user: discord.abc.Snowflake) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                '''
                DELETE FROM users WHERE user_id = ?
                ''',
                (user.id,),
            )

    async def get_name(self, user: discord.abc.Snowflake) -> Optional[str]:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                '''
                SELECT name FROM users WHERE user_id = ?
                ''',
                (user.id,),
            )
            data = await cursor.fetchone()

            if data is not None:
                return data['name']
