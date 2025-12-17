from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import psycopg2

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: str
    phone_number: Optional[str] = None
    password_hash: str
    subscription_status: bool = False

class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    subscription_status: Optional[bool] = None

class FavoriteParkingAdd(BaseModel):
    id_user: int
    id_parking: int

@router.get("/users/all")
def get_all_users():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, phone_number, subscription_status FROM users;")
                return cur.fetchall()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/user/{user_id}")
def get_user(user_id: int):
    try:
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
                row = cur.fetchone()
                if row is None:
                    return {"error": "User not found"}
        return row
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/user_fields/{user_id}")
def get_user_fields(user_id: int, fields: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                selected = ",".join([f.strip() for f in fields.split(",")])
                cur = conn.cursor()
                cur.execute(f"SELECT {selected} FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if row is None:
                    return {"error": "User not found"}
        result = dict(zip(selected.split(","), row))
        return result
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/users")
def create_user(user: UserCreate):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="Email already exists")

                hashed_password = pwd_context.hash(user.password_hash)

                cur.execute(
                    """
                    INSERT INTO users (email, phone_number, password_hash, subscription_status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, email, phone_number, subscription_status;
                    """,
                    (user.email, user.phone_number, hashed_password, user.subscription_status)
                )
                created_user = cur.fetchone()
                conn.commit()

        fields = ["id", "email", "phone_number", "subscription_status"]
        return dict(zip(fields, created_user))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


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

    try:
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
                if updated is None:
                    raise HTTPException(status_code=404, detail="User not found")

                conn.commit()
        fields = ["id", "email", "phone_number", "subscription_status"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/user/{user_id}", status_code=204)
def delete_user(user_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
                deleted = cur.fetchone()
                if deleted is None:
                    raise HTTPException(status_code=404, detail="User not found")
            conn.commit()
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to delete user")

@router.get("/users/stats")
def get_users_stats():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
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
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")
