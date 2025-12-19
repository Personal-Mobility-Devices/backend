from database import get_db_connection


class FavoriteParkingsDAO:
    @staticmethod
    def get(user_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.id, p.name, p.coordinates
                    FROM favorite_parkings fp
                    JOIN parkings p ON p.id = fp.id_parking
                    WHERE fp.id_user = %s;
                    """,
                    (user_id,)
                )
                return cur.fetchall()

    @staticmethod
    def add(id_user: int, id_parking: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO favorite_parkings (id_user, id_parking)
                    VALUES (%s, %s)
                    RETURNING id;
                    """,
                    (id_user, id_parking)
                )
                fav = cur.fetchone()
                conn.commit()
                return fav

    @staticmethod
    def delete(id_user: int, id_parking: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM favorite_parkings
                    WHERE id_user = %s AND id_parking = %s
                    RETURNING id;
                    """,
                    (id_user, id_parking)
                )
                deleted = cur.fetchone()
                conn.commit()
                return deleted
