import os
import psycopg2

# Глобальная переменная для хранения подключения
_connection = None

def get_db_connection():
    """Создает или возвращает существующее подключение к базе данных.
    Использует DATABASE_URL (для Render) или отдельные переменные."""
    global _connection
    
    if _connection is None or _connection.closed:
        # Если есть DATABASE_URL (Render автоматически предоставляет её)
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Render иногда использует postgres:// вместо postgresql://
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            
            _connection = psycopg2.connect(database_url)
        else:
            # Если DATABASE_URL нет, используем отдельные переменные (для локальной разработки)
            _connection = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "parkings_db"),
                user=os.getenv("DB_USER", "parkings_db_user"),
                password=os.getenv("DB_PASSWORD", "dxUVHnV0sqULLO73J2dxZETqne4feSK9"),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432")
            )
    
    return _connection

