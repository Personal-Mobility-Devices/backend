import psycopg2
from fastapi import HTTPException

from database import get_db_connection


class ParkingSpaceDAO:
    @staticmethod
    async def get_all():
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM parking_spaces;")

    @staticmethod
    async def get_by_id(space_id: str):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            # asyncpg умеет работать с UUID напрямую
            return await conn.fetchrow("SELECT * FROM parking_spaces WHERE id = $1", space_id)

    @staticmethod
    async def get_all_by_parking_id(parking_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM parking_spaces WHERE id_parking = $1", parking_id)

    @staticmethod
    async def create(coordinates: str, id_parking: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            query = """
                INSERT INTO parking_spaces (coordinates, id_parking)
                VALUES ($1, $2)
                RETURNING id, id_parking;
            """
            try:
                return await conn.fetchrow(query, coordinates, id_parking)
            except psycopg2.errors.ForeignKeyViolation:
                raise HTTPException(status_code=404, detail="Parent Parking ID not found")

    @staticmethod
    async def update(space_id: str, coordinates: str):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            query = """
                UPDATE parking_spaces
                SET coordinates = $1
                WHERE id = $2
                RETURNING id, id_parking;
            """
            return await conn.fetchrow(query, coordinates, space_id)

    @staticmethod
    async def delete(space_id: str):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                "DELETE FROM parking_spaces WHERE id = $1 RETURNING id;",
                space_id
            )
