import psycopg2
from fastapi import HTTPException

from database import get_db_connection


class ParkingSpaceDAO:
    @staticmethod
    def get_all():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM parking_spaces;")
                return cur.fetchall()

    @staticmethod
    def get_by_id(space_id: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # psycopg2 умеет работать с UUID напрямую
                cur.execute("SELECT * FROM parking_spaces WHERE id = %s", (space_id,))
                return cur.fetchone()

    @staticmethod
    def get_all_by_parking_id(parking_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM parking_spaces WHERE id_parking = %s", (parking_id,))
                return cur.fetchall()

    @staticmethod
    def create(coordinates: str, id_parking: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO parking_spaces (coordinates, id_parking)
                    VALUES (%s, %s)
                    RETURNING id, id_parking;
                """
                try:
                    cur.execute(query, (coordinates, id_parking))
                    created_space = cur.fetchone()
                    conn.commit()
                    return created_space
                except psycopg2.errors.ForeignKeyViolation:
                    conn.rollback()
                    raise HTTPException(status_code=404, detail="Parent Parking ID not found")

    @staticmethod
    def update(space_id: str, coordinates: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    UPDATE parking_spaces
                    SET coordinates = %s
                    WHERE id = %s
                    RETURNING id, id_parking;
                """
                cur.execute(query, (coordinates, space_id))
                updated = cur.fetchone()
                conn.commit()
                return updated

    @staticmethod
    def delete(space_id: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM parking_spaces WHERE id = %s RETURNING id;",
                    (space_id,)
                )
                deleted = cur.fetchone()
                conn.commit()
                return deleted
