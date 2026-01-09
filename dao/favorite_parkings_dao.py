from database import get_db_connection


class FavoriteParkingsDAO:
    @staticmethod
    async def get(user_id: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT p.id, p.name, p.coordinates
                FROM favorite_parkings fp
                JOIN parkings p ON p.id = fp.id_parking
                WHERE fp.id_user = $1;                
                """,
                user_id
            )

    @staticmethod
    async def add(id_user: int, id_parking: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                INSERT INTO favorite_parkings (id_user, id_parking)
                VALUES ($1, $2)
                RETURNING id;                
                """,
                id_user,
                id_parking
            )

    @staticmethod
    async def delete(id_user: int, id_parking: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow(
                """
                DELETE FROM favorite_parkings
                WHERE id_user = $1 AND id_parking = $2
                RETURNING id;                
                """,
                id_user,
                id_parking
            )
