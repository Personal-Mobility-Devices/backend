import psycopg2
from fastapi import HTTPException

from database import get_db_connection


class ParkingSpaceDAO:

    @staticmethod
    def get_all():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        id_parking
                    FROM parking_spaces
                """)
                rows = cur.fetchall()
                return [
                    {"id": str(r[0]), "coordinates": {"lon": r[1], "lat": r[2]}, "id_parking": r[3]}
                    for r in rows
                ]

    @staticmethod
    def get_by_id(space_id: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        id_parking
                    FROM parking_spaces
                    WHERE id = %s
                """, (space_id,))
                row = cur.fetchone()
                if row is None:
                    return None
                return {"id": str(row[0]), "coordinates": {"lon": row[1], "lat": row[2]}, "id_parking": row[3]}

    @staticmethod
    def get_all_by_parking_id(parking_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        id_parking
                    FROM parking_spaces
                    WHERE id_parking = %s
                """, (parking_id,))
                rows = cur.fetchall()
                return [
                    {"id": str(r[0]), "coordinates": {"lon": r[1], "lat": r[2]}, "id_parking": r[3]}
                    for r in rows
                ]

    @staticmethod
    def create(lat: float, lon: float, id_parking: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO parking_spaces (coordinates, id_parking)
                    VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
                    RETURNING
                        id,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        id_parking
                """
                try:
                    cur.execute(query, (lon, lat, id_parking))
                    row = cur.fetchone()
                    conn.commit()
                    return {"id": str(row[0]), "coordinates": {"lon": row[1], "lat": row[2]}, "id_parking": row[3]}
                except psycopg2.errors.ForeignKeyViolation:
                    conn.rollback()
                    raise HTTPException(status_code=404, detail="Parent Parking ID not found")

    @staticmethod
    def update(space_id: str, lat: float, lon: float):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE parking_spaces
                    SET coordinates = ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    WHERE id = %s
                    RETURNING
                        id,
                        ST_X(coordinates) AS lon,
                        ST_Y(coordinates) AS lat,
                        id_parking
                """, (lon, lat, space_id))
                row = cur.fetchone()
                conn.commit()
                if row is None:
                    return None
                return {"id": str(row[0]), "coordinates": {"lon": row[1], "lat": row[2]}, "id_parking": row[3]}

    @staticmethod
    def delete(space_id: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM parking_spaces WHERE id = %s RETURNING id",
                    (space_id,)
                )
                deleted = cur.fetchone()
                conn.commit()
                return deleted