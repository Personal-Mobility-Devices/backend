from typing import Optional

from fastapi import HTTPException

from database import get_db_connection


class ParkingsDAO:

    @staticmethod
    async def get_all():
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
                FROM parkings;                
                """
            )

    @staticmethod
    async def get_in_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            query = """
                SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
                FROM parkings
                WHERE (coordinates->>'lat')::float BETWEEN $1 AND $2
                AND   (coordinates->>'lon')::float BETWEEN $3 AND $4;
            """
            return await conn.fetch(query, lat_min, lat_max, lon_min, lon_max)

    @staticmethod
    async def get_by_id(parking_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
                FROM parkings
                WHERE id = $1                
                """,
                parking_id
            )

    @staticmethod
    async def get_fields(parking_id: int, selected_fields: str):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(f"SELECT {selected_fields} FROM parkings WHERE id = $1", parking_id)

    @staticmethod
    async def get_geojson(parking_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
                FROM parkings
                WHERE id = $1                
                """,
                parking_id
            )

    @staticmethod
    async def create(
            description: str,
            coordinates: str,
            name: Optional[str] = None,
            name_obj: Optional[str] = None,
            adm_area: Optional[str] = None,
            district: Optional[str] = None,
            occupancy: Optional[str] = None  # В БД строка, возможно позже изменим на int
    ):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            query = """
                INSERT INTO parkings (description, coordinates, name, name_obj, adm_area, district, occupancy)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, name, coordinates;
            """
            try:
                return await conn.fetchrow(
                    query,
                    description,
                    coordinates,
                    name,
                    name_obj,
                    adm_area,
                    district,
                    occupancy
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def update(updates: list[str], where_idx: int, params: list):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            query = f"""
                UPDATE parkings
                SET {", ".join(updates)}
                WHERE id = ${where_idx}
                RETURNING id, name, occupancy;
            """
            updated = await conn.fetchrow(query, *params)

            if updated is None:
                raise HTTPException(status_code=404, detail="Parking not found")

            return updated

    @staticmethod
    async def delete(parking_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:

            deleted = await conn.fetchrow(
                """
                DELETE FROM parkings
                WHERE id = $1
                RETURNING id;
                """,
                parking_id)

            if deleted is None:
                raise HTTPException(status_code=404, detail="Parking not found")

            return deleted
