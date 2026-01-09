import os
import asyncpg

pool: asyncpg.Pool | None = None

def build_dsn() -> str:
    # Если есть DATABASE_URL (Render автоматически предоставляет её)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://", "postgresql://", 1
            )
        return database_url

    # Если DATABASE_URL нет, используем отдельные переменные (для локальной разработки)
    return (
        f"postgresql://"
        f"{os.getenv('DB_USER', 'parkings_db_user')}:"
        f"{os.getenv('DB_PASSWORD', 'dxUVHnV0sqULLO73J2dxZETqne4feSK9')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'parkings_db')}"
    )


async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        dsn=build_dsn(),
        min_size=1,
        max_size=10
    )


async def close_db():
    global pool
    if pool:
        await pool.close()


async def get_db_connection():
    if pool is None:
        raise RuntimeError("DB pool is not initialized")
    return pool
