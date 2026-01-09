import psycopg2
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext

from dao.users_dao import UsersDAO
from schemas.userModels import UserCreate, UserUpdate

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/users/all")
async def get_all_users():
    try:
        return await UsersDAO.get_all()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/user/{user_id}")
async def get_user(user_id: int):
    try:
        row = await UsersDAO.get(user_id)
        if row is None:
            return {"error": "User not found"}
        return row
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/user_fields/{user_id}")
async def get_user_fields(user_id: int, fields: str):
    try:
        selected = ",".join([f.strip() for f in fields.split(",")])
        row = await UsersDAO.get_fields(user_id, selected)
        if row is None:
            return {"error": "User not found"}
        result = dict(zip(selected.split(","), row))
        return result
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/users")
async def create_user(user: UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password_hash)
        created_user = await UsersDAO.create(user.email, hashed_password, user.phone_number, user.subscription_status)
        fields = ["id", "email", "phone_number", "subscription_status"]
        return dict(zip(fields, created_user))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/user/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    updates = []
    params = []
    idx = 1

    if user.phone_number is not None:
        updates.append(f"phone_number = ${idx}")
        params.append(user.phone_number)
        idx += 1
    if user.subscription_status is not None:
        updates.append(f"subscription_status = ${idx}")
        params.append(user.subscription_status)
        idx += 1

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(user_id)

    # В asyncpg нет %s, как это было в psycopg2, для передачи аргументов используется %1, %2 и так далее
    where_idx = idx  # текущий порядковый номер idx для аргумента

    try:
        updated = await UsersDAO.update(updates, where_idx, params)
        if updated is None:
            raise HTTPException(status_code=404, detail="User not found")
        fields = ["id", "email", "phone_number", "subscription_status"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/user/{user_id}", status_code=204)
async def delete_user(user_id: int):
    try:
        deleted = await UsersDAO.delete(user_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="User not found")
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to delete user")


@router.get("/users/stats")
async def get_users_stats():
    try:
        total, subscribers = await UsersDAO.get_stats()
        subscribers = subscribers or 0
        share = (subscribers / total) if total else 0.0
        return {
            "total_users": total,
            "subscribers": subscribers,
            "subscription_share": share
        }
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")
