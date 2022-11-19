from typing import List, Optional

import aiosqlite
import discord


class Database:
    conn: aiosqlite.Connection

    async def setup_hook(self) -> None:
        self.conn = await aiosqlite.connect('verification.db')
        await self.init()

    async def close(self) -> None:
        await self.conn.close()

    async def init(self) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (user_id int, name text)
                '''
            )
            await cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS messages (message_id)
                '''
            )
        await self.conn.commit()

    async def insert_user(self, user: discord.abc.Snowflake, name: str) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                '''
                INSERT INTO users VALUES (?, ?)
                ''',
                (user.id, name),
            )
        await self.conn.commit()

    async def remove_user(self, user: discord.abc.Snowflake) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                '''
                DELETE FROM users WHERE user_id = ?
                ''',
                (user.id,),
            )
        await self.conn.commit()

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
                return data[0]

    async def insert_message(self, message: discord.abc.Snowflake) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                '''
                INSERT INTO messages VALUES (?)
                ''',
                (message.id,),
            )
        await self.conn.commit()

    async def remove_message(self, message: discord.abc.Snowflake) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                '''
                DELETE FROM messages WHERE message_id = ?
                ''',
                (message.id,),
            )
        await self.conn.commit()

    async def get_messages(self) -> List[int]:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                '''
                SELECT message_id FROM messages
                '''
            )
            return [data[0] for data in await cursor.fetchall()]
