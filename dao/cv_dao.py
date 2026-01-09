from database import get_db_connection


class CvDAO:

    @staticmethod
    async def get_data(id_cam: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow("SELECT cv_data FROM cameras WHERE id = $1", id_cam)

    @staticmethod
    async def update_occupancy(id_parking: int, occupancy: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            # Возвращает строки вида "UPDATE 3" - берем число строк из строки и преобразуем в int
            result = conn.execute("UPDATE parkings SET occupancy = $1 WHERE id = $2", occupancy, id_parking)
            row_count = int(result.split()[-1])
            return row_count

    @staticmethod
    async def get_status(id_parking: int):
        pool = await get_db_connection()
        async with pool.acquire() as conn:
            return await conn.fetchrow("SELECT occupancy FROM parkings WHERE id = $1", id_parking)
