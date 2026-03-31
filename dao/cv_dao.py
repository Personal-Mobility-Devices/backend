from database import get_db_connection


class CvDAO:

    @staticmethod
    def get_data():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT cv_data FROM cameras")
                return cur.fetchall()

    @staticmethod
    def update_occupancy(id_parking: int, occupancy: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE parkings SET occupancy = %s WHERE id = %s",
                    (occupancy, id_parking)
                )
                row_count = cur.rowcount
                conn.commit()
                return row_count

    @staticmethod
    def get_status(id_parking: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT occupancy FROM parkings WHERE id = %s",
                    (id_parking,)
                )
                return cur.fetchone()
