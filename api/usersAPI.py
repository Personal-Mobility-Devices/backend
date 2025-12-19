from typing import Optional

import psycopg2
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel

from dao.users_dao import UsersDAO

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
        return UsersDAO.get_all()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/user/{user_id}")
def get_user(user_id: int):
    try:
        row = UsersDAO.get(user_id)
        if row is None:
            return {"error": "User not found"}
        return row
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/user_fields/{user_id}")
def get_user_fields(user_id: int, fields: str):
    try:
        selected = ",".join([f.strip() for f in fields.split(",")])
        row = UsersDAO.get_fields(user_id, selected)
        if row is None:
            return {"error": "User not found"}
        result = dict(zip(selected.split(","), row))
        return result
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/users")
def create_user(user: UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password_hash)
        created_user = UsersDAO.create(user.email, hashed_password, user.phone_number, user.subscription_status)
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
        updated = UsersDAO.update(updates, params)
        if updated is None:
            raise HTTPException(status_code=404, detail="User not found")
        fields = ["id", "email", "phone_number", "subscription_status"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/user/{user_id}", status_code=204)
def delete_user(user_id: int):
    try:
        deleted = UsersDAO.delete(user_id)
        if deleted is None:
            raise HTTPException(status_code=404, detail="User not found")
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to delete user")


@router.get("/users/stats")
def get_users_stats():
    try:
        total, subscribers = UsersDAO.get_stats()
        subscribers = subscribers or 0
        share = (subscribers / total) if total else 0.0
        return {
            "total_users": total,
            "subscribers": subscribers,
            "subscription_share": share
        }
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")
