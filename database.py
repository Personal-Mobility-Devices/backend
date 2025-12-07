import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "parkings_db"),
        user=os.getenv("DB_USER", "parkings_db_user"),
        password=os.getenv("DB_PASSWORD", "dxUVHnV0sqULLO73J2dxZETqne4feSK9"),
        host=os.getenv("DB_HOST", "dpg-d4qo7p3uibrs739lch3g-a.virginia-postgres.render.com"),
        port=os.getenv("DB_PORT", "5432")
    )

