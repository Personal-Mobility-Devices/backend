from typing import Dict, Any

from psycopg2._json import Json

from database import get_db_connection


class CamerasDAO:

    @staticmethod
    def get_all():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, description, cv_data FROM cameras;")
                return cur.fetchall()

    @staticmethod
    def get_camera(camera_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, description, cv_data FROM cameras WHERE id = %s;",
                    (camera_id,)
                )
                return cur.fetchone()

    @staticmethod
    def create(description: str, cv_data: Dict[str, Any]):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cameras (description, cv_data)
                    VALUES (%s, %s)
                    RETURNING id, description, cv_data;
                    """,
                    (description, Json(cv_data))
                )
                created = cur.fetchone()
                conn.commit()
                return created

    @staticmethod
    def delete(camera_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM cameras WHERE id = %s RETURNING id;",
                    (camera_id,)
                )
                deleted = cur.fetchone()
                conn.commit()
                return deleted

    @staticmethod
    def update(updates: list[str], params: list):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE cameras
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, description, cv_data;
                    """,
                    params
                )
                updated = cur.fetchone()
                conn.commit()
                return updated
