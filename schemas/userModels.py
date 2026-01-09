from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    phone_number: Optional[str] = None
    password_hash: str
    subscription_status: bool = False


class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    subscription_status: Optional[bool] = None
