from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    db_name: str = Field(default="parkings_db", alias="DB_NAME")
    db_user: str = Field(default="parkings_db_user", alias="DB_USER")
    db_password: str = Field(default="dxUVHnV0sqULLO73J2dxZETqne4feSK9", alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: str = Field(default="5432", alias="DB_PORT")
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    jwt_secret: str = Field(default="change_me", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALG")
    jwt_access_expires_minutes: int = Field(default=15, alias="JWT_ACCESS_EXPIRES_MIN")
    jwt_refresh_expires_days: int = Field(default=7, alias="JWT_REFRESH_EXPIRES_DAYS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
