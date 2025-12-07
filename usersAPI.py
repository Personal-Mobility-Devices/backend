from fastapi import APIRouter, HTTPException
import psycopg2
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

conn = psycopg2.connect(
    dbname="parkings_db",
    user="postgres",
    password="228336",
    host="localhost",
    port="5432"
)

class UserCreate(BaseModel):
    email: str
    phone_number: Optional[str] = None
    password_hash: str
    subscription_status: bool = False

class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    subscription_status: Optional[bool] = None


@router.get("/users/all")
def get_all_users():
    cur = conn.cursor()
    cur.execute("SELECT id, email, phone_number, subscription_status FROM users;")
    return cur.fetchall()


@router.get("/user/{user_id}")
def get_user(user_id: int):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, email, phone_number, subscription_status
        FROM users
        WHERE id = %s
        """,
        (user_id,)
    )
    row = cur.fetchone()
    if row is None:
        return {"error": "User not found"}
    return row


@router.get("/user_fields/{user_id}")
def get_user_fields(user_id: int, fields: str):
    selected = ",".join([f.strip() for f in fields.split(",")])
    cur = conn.cursor()
    cur.execute(f"SELECT {selected} FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    if row is None:
        return {"error": "User not found"}
    result = dict(zip(selected.split(","), row))
    return result


@router.post("/users")
def create_user(user: UserCreate):
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Email already exists")

    cur.execute(
        """
        INSERT INTO users (email, phone_number, password_hash, subscription_status)
        VALUES (%s, %s, %s, %s)
        RETURNING id, email, phone_number, subscription_status;
        """,
        (user.email, user.phone_number, user.password_hash, user.subscription_status)
    )
    created_user = cur.fetchone()
    conn.commit()

    fields = ["id", "email", "phone_number", "subscription_status"]
    return dict(zip(fields, created_user))


@router.put("/user/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    updates = []
    params = []

    if user.phone_number is not None:
        updates.append("phone_number = %s")
        params.append(user.phone_number)
    if user.subscription_status is not None:
        updates.append("subscription_status = %s")
        params.append(user.subscription_status)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(user_id)

    cur = conn.cursor()
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
    if updated is None:
        raise HTTPException(status_code=404, detail="User not found")

    conn.commit()
    fields = ["id", "email", "phone_number", "subscription_status"]
    return dict(zip(fields, updated))


@router.delete("/user/{user_id}", status_code=204)
def delete_user(user_id: int):
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
    deleted = cur.fetchone()
    if deleted is None:
        raise HTTPException(status_code=404, detail="User not found")
    conn.commit()


@router.get("/users/stats")
def get_users_stats():
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN subscription_status THEN 1 ELSE 0 END) AS subscribers
        FROM users;
        """
    )
    total, subscribers = cur.fetchone()
    subscribers = subscribers or 0
    share = (subscribers / total) if total else 0.0
    return {
        "total_users": total,
        "subscribers": subscribers,
        "subscription_share": share
    }


@router.get("/users/{user_id}/favorites")
def get_user_favorites(user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")

    query = """
        SELECT p.id, p.name, p.coordinates
        FROM favorite_parkings fp
        JOIN parkings p ON p.id = fp.id_parking
        WHERE fp.id_user = %s;
    """
    cur.execute(query, (user_id,))
    return cur.fetchall()
