from typing import List, Tuple, Optional
from database import get_db_connection
from schemas.simStopsModels import SIMStopUpdate

class SimStopsDAO:
    @staticmethod
    def get_all() -> List[Tuple]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        description,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        adm_area,
                        district,
                        free_sim_count
                    FROM sim_stops
                    ORDER BY id
                """)
                return cur.fetchall()

    @staticmethod
    def get_by_id(stop_id: int) -> Optional[Tuple]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        description,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        adm_area,
                        district,
                        free_sim_count
                    FROM sim_stops
                    WHERE id = %s
                """, (stop_id,))
                return cur.fetchone()

    @staticmethod
    def get_in_area(lat_min: float, lat_max: float,
                    lon_min: float, lon_max: float) -> List[Tuple]:
        """
        Поиск остановок СИМ в прямоугольной зоне видимости.
        Используем ST_MakeEnvelope + ST_Within для точного попадания в bbox.
        ST_MakeEnvelope(xmin, ymin, xmax, ymax, srid) — т.е. (lon_min, lat_min, lon_max, lat_max)
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        description,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        adm_area,
                        district,
                        free_sim_count
                    FROM sim_stops
                    WHERE coordinates && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
                      AND ST_Within(coordinates, ST_MakeEnvelope(%s, %s, %s, %s, 4326))
                """, (lon_min, lat_min, lon_max, lat_max,
                      lon_min, lat_min, lon_max, lat_max))
                return cur.fetchall()

    @staticmethod
    def create(
        description: Optional[str],
        lat: float,
        lon: float,
        adm_area: Optional[str],
        district: Optional[str],
        free_sim_count: int = 0
    ) -> Tuple:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sim_stops (description, coordinates, adm_area, district, free_sim_count)
                    VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s)
                    RETURNING
                        id,
                        description,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        adm_area,
                        district,
                        free_sim_count
                """, (description, lon, lat, adm_area, district, free_sim_count))
                conn.commit()
                return cur.fetchone()

    @staticmethod
    def update(stop_id: int, stop_update: SIMStopUpdate) -> Optional[Tuple]:
        updates = []
        params = []

        if stop_update.description is not None:
            updates.append("description = %s")
            params.append(stop_update.description)

        if stop_update.coordinates is not None:
            updates.append("coordinates = ST_SetSRID(ST_MakePoint(%s, %s), 4326)")
            params.append(stop_update.coordinates.lon)
            params.append(stop_update.coordinates.lat)

        if stop_update.adm_area is not None:
            updates.append("adm_area = %s")
            params.append(stop_update.adm_area)

        if stop_update.district is not None:
            updates.append("district = %s")
            params.append(stop_update.district)

        if stop_update.free_sim_count is not None:
            updates.append("free_sim_count = %s")
            params.append(stop_update.free_sim_count)

        if not updates:
            return SimStopsDAO.get_by_id(stop_id)

        params.append(stop_id)

        query = f"""
            UPDATE sim_stops
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING
                id,
                description,
                ST_X(coordinates) AS lon,
                ST_Y(coordinates) AS lat,
                adm_area,
                district,
                free_sim_count
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.fetchone()

    @staticmethod
    def delete(stop_id: int) -> Optional[Tuple]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM sim_stops WHERE id = %s RETURNING id",
                    (stop_id,)
                )
                conn.commit()
                return cur.fetchone()