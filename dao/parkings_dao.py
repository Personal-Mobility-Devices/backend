from typing import Optional

from fastapi import HTTPException

from database import get_db_connection


class ParkingsDAO:

    @staticmethod
    def get_all():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
                    FROM parkings;
                """)
                return cur.fetchall()

    @staticmethod
    def get_in_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
                    FROM parkings
                    WHERE (coordinates->>'lat')::float BETWEEN %s AND %s
                    AND   (coordinates->>'lon')::float BETWEEN %s AND %s;
                """
                cur.execute(query, (lat_min, lat_max, lon_min, lon_max))
                return cur.fetchall()

    @staticmethod
    def get_by_id(parking_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
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
                    SELECT id, description, coordinates, name, name_obj, adm_area, district, occupancy
                    FROM parkings
                    WHERE id = %s
                """, (parking_id,))

                return cur.fetchone()

    @staticmethod
    def create(
            description: str,
            coordinates: str,
            name: Optional[str] = None,
            name_obj: Optional[str] = None,
            adm_area: Optional[str] = None,
            district: Optional[str] = None,
            occupancy: Optional[str] = None  # В БД строка, возможно позже изменим на int
    ):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO parkings (description, coordinates, name, name_obj, adm_area, district, occupancy)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, name, coordinates;
                """
                try:
                    cur.execute(query, (
                        description,
                        coordinates,
                        name,
                        name_obj,
                        adm_area,
                        district,
                        occupancy
                    ))
                    created_parking = cur.fetchone()
                    conn.commit()
                    return created_parking
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
                    RETURNING id, name, occupancy;
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
                    RETURNING id;
                """, (parking_id,))

                deleted = cur.fetchone()
                conn.commit()

                if deleted is None:
                    raise HTTPException(status_code=404, detail="Parking not found")

                return deleted
