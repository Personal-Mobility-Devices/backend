import psycopg2
from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext

from auth import create_access_token, create_refresh_token, decode_refresh_token
from dao.users_dao import UsersDAO
from schemas.authModels import RefreshToken, UserLogin

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/auth/login")
def login(user: UserLogin):
    try:
        row = UsersDAO.get_auth_data(user.email)
        if row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        user_id, password_hash = row
        if not pwd_context.verify(user.password, password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id),
            "token_type": "bearer",
        }
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/auth/refresh")
def refresh(payload: RefreshToken):
    user_id = decode_refresh_token(payload.refresh_token)
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
    }
