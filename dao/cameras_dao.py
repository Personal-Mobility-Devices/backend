from typing import Dict, Any

from psycopg2._json import Json

from database import get_db_connection


class CamerasDAO:

    @staticmethod
    async def get_all():
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetch("SELECT id, description, cv_data FROM cameras;")

    @staticmethod
    async def get_camera(camera_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT id, description, cv_data FROM cameras WHERE id = $1;",
                camera_id
            )

    @staticmethod
    async def create(description: str, cv_data: Dict[str, Any]):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO cameras (description, cv_data)
                VALUES ($1, $2)
                RETURNING id, description, cv_data;
                """,
                description,
                Json(cv_data)
            )

    @staticmethod
    async def delete(camera_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                "DELETE FROM cameras WHERE id = $1 RETURNING id;",
                camera_id
            )

    @staticmethod
    async def update(updates: list[str], where_idx: int, params: list):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                f"""
                UPDATE cameras
                SET {", ".join(updates)}
                WHERE id = ${where_idx}
                RETURNING id, description, cv_data;
                """,
                *params
            )
