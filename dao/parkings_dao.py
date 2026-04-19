import json
from typing import Optional

from fastapi import HTTPException

from database import get_db_connection


class ParkingsDAO:

    @staticmethod
    def get_all():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        description,
                        ST_AsGeoJSON(coordinates) AS coordinates,
                        name,
                        name_obj,
                        adm_area,
                        district,
                        occupancy,
                        all_spaces
                    FROM parkings
                """)
                return cur.fetchall()

    @staticmethod
    def get_in_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float):
        """Поиск парковок в прямоугольной зоне через PostGIS ST_Within."""
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        description,
                        ST_AsGeoJSON(coordinates) AS coordinates,
                        name,
                        name_obj,
                        adm_area,
                        district,
                        occupancy,
                        all_spaces
                    FROM parkings
                    WHERE ST_Intersects(coordinates, ST_MakeEnvelope(%s, %s, %s, %s, 4326))
                """, (lon_min, lat_min, lon_max, lat_max))
                return cur.fetchall()

    @staticmethod
    def get_by_id(parking_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        description,
                        ST_AsGeoJSON(coordinates) AS coordinates,
                        name,
                        name_obj,
                        adm_area,
                        district,
                        occupancy,
                        all_spaces
                    FROM parkings
                    WHERE id = %s
                """, (parking_id,))
                return cur.fetchone()

    @staticmethod
    def get_fields(parking_id: int, selected_fields: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {selected_fields} FROM parkings WHERE id = %s", (parking_id,))
                return cur.fetchone()

    @staticmethod
    def get_geojson(parking_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        description,
                        ST_AsGeoJSON(coordinates) AS coordinates,
                        name,
                        name_obj,
                        adm_area,
                        district,
                        occupancy,
                        all_spaces
                    FROM parkings
                    WHERE id = %s
                """, (parking_id,))
                return cur.fetchone()

    @staticmethod
    def create(
            description: str,
            coords: list,
            name: Optional[str] = None,
            name_obj: Optional[str] = None,
            adm_area: Optional[str] = None,
            district: Optional[str] = None,
            occupancy: Optional[int] = None,
            all_spaces: Optional[int] = None
    ):
        if coords[0] != coords[-1]:
            coords = coords + [coords[0]]
        geojson_str = json.dumps({"type": "Polygon", "coordinates": [coords]})
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO parkings (description, coordinates, name, name_obj, adm_area, district, occupancy, all_spaces)
                    VALUES (%s, ST_GeomFromGeoJSON(%s), %s, %s, %s, %s, %s, %s)
                    RETURNING
                        id,
                        name,
                        ST_AsGeoJSON(coordinates) AS coordinates
                """
                try:
                    cur.execute(query, (description, geojson_str, name, name_obj, adm_area, district, occupancy, all_spaces))
                    created = cur.fetchone()
                    conn.commit()
                    return created
                except Exception as e:
                    conn.rollback()
                    raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def update(updates: list[str], params: list):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = f"""
                    UPDATE parkings
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, name, occupancy
                """
                cur.execute(query, params)
                updated = cur.fetchone()
                conn.commit()

                if updated is None:
                    raise HTTPException(status_code=404, detail="Parking not found")

                return updated

    @staticmethod
    def delete(parking_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM parkings
                    WHERE id = %s
                    RETURNING id
                """, (parking_id,))
                deleted = cur.fetchone()
                conn.commit()

                if deleted is None:
                    raise HTTPException(status_code=404, detail="Parking not found")

                return deleted