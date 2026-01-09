from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class RefreshToken(BaseModel):
    refresh_token: str
