from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
import psycopg2

router = APIRouter()

class FavoriteParkingAdd(BaseModel):
    id_user: int
    id_parking: int

@router.get("/favorites/{user_id}")
def get_favorites(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT p.id, p.name, p.coordinates
        FROM favorite_parkings fp
        JOIN parkings p ON p.id = fp.id_parking
        WHERE fp.id_user = %s;
    """
    cur.execute(query, (user_id,))
    return cur.fetchall()

@router.post("/favorites", status_code=201)
def add_favorite_parking(fav_data: FavoriteParkingAdd):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO favorite_parkings (id_user, id_parking)
        VALUES (%s, %s)
        RETURNING id;
    """
    try:
        cur.execute(query, (fav_data.id_user, fav_data.id_parking))
        fav_id = cur.fetchone()[0]
        conn.commit()
        return {"id": fav_id, "message": "Parking added to favorites"}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Parking is already in user's favorites")
    except psycopg2.errors.ForeignKeyViolation as e:
        conn.rollback()
        # Определяем, какой внешний ключ нарушен, чтобы дать точный ответ
        if "fk_fav_user" in str(e):
            raise HTTPException(status_code=404, detail="User not found")
        if "fk_fav_parking" in str(e):
            raise HTTPException(status_code=404, detail="Parking not found")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()


@router.delete("/favorites", status_code=204)
def remove_favorite_parking(id_user: int, id_parking: int):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        DELETE FROM favorite_parkings
        WHERE id_user = %s AND id_parking = %s
        RETURNING id;
    """
    cur.execute(query, (id_user, id_parking))
    deleted = cur.fetchone()
    conn.commit()

    if deleted is None:
        raise HTTPException(status_code=404, detail="Favorite relationship not found")