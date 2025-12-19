from typing import Optional

from fastapi import HTTPException

from database import get_db_connection


class UsersDAO:

    @staticmethod
    def get_all():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, phone_number, subscription_status FROM users;")
                return cur.fetchall()

    @staticmethod
    def get(user_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, phone_number, subscription_status
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
                )
                return cur.fetchone()

    @staticmethod
    def get_fields(user_id: int, selected_fields: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {selected_fields} FROM users WHERE id = %s", (user_id,))
                return cur.fetchone()

    @staticmethod
    def create(
            email: str,
            hashed_password: str,
            phone_number: Optional[str] = None,
            subscription_status: bool = False
    ):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="Email already exists")

                cur.execute(
                    """
                    INSERT INTO users (email, phone_number, password_hash, subscription_status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, email, phone_number, subscription_status;
                    """,
                    (email, phone_number, hashed_password, subscription_status)
                )
                created_user = cur.fetchone()
                conn.commit()
                return created_user

    @staticmethod
    def update(updates: list[str], params: list):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE users
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, email, phone_number, subscription_status;
                    """,
                    params
                )
                updated = cur.fetchone()
                conn.commit()
                return updated

    @staticmethod
    def delete(user_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
                deleted = cur.fetchone()
                conn.commit()
                return deleted

    @staticmethod
    def get_stats():
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) AS total,
                           SUM(CASE WHEN subscription_status THEN 1 ELSE 0 END) AS subscribers
                    FROM users;
                    """
                )
                return cur.fetchone()
