from typing import Optional

from fastapi import HTTPException

from database import get_db_connection


class UsersDAO:

    @staticmethod
    async def get_all():
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetch("SELECT id, email, phone_number, subscription_status FROM users;")

    @staticmethod
    async def get(user_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT id, email, phone_number, subscription_status
                FROM users
                WHERE id = $1                
                """,
                user_id
            )

    @staticmethod
    async def get_fields(user_id: int, selected_fields: str):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(f"SELECT {selected_fields} FROM users WHERE id = $1", user_id)

    @staticmethod
    async def create(
            email: str,
            hashed_password: str,
            phone_number: Optional[str] = None,
            subscription_status: bool = False
    ):
        pool = await get_db_connection()
        async with pool.acquire() as conn:

            if conn.fetchrow("SELECT id FROM users WHERE email = $1", email):
                raise HTTPException(status_code=400, detail="Email already exists")

            return await conn.fetchrow(
                """
                INSERT INTO users (email, phone_number, password_hash, subscription_status)
                VALUES ($1, $2, $3, $4)
                RETURNING id, email, phone_number, subscription_status;                
                """,
                email,
                phone_number,
                hashed_password,
                subscription_status
            )

    @staticmethod
    async def update(updates: list[str], where_idx: int, params: list):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                f"""
                UPDATE users
                SET {", ".join(updates)}
                WHERE id = ${where_idx}
                RETURNING id, email, phone_number, subscription_status;                
                """,
                *params
            )

    @staticmethod
    async def delete(user_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow("DELETE FROM users WHERE id = $1 RETURNING id;", user_id)

    @staticmethod
    async def get_stats():
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN subscription_status THEN 1 ELSE 0 END) AS subscribers
                FROM users;                
                """
            )
