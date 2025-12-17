from fastapi import APIRouter, HTTPException
from database import get_db_connection
from pydantic import BaseModel
from typing import Optional
import psycopg2


router = APIRouter()

class Coordinates(BaseModel):
    lat: float
    lon: float

class ParkingSpaceCreate(BaseModel):
    coordinates: Coordinates
    id_parking: int

class ParkingSpaceUpdate(BaseModel):
    coordinates: Optional[Coordinates] = None


@router.get("/parking_spaces/all")
def get_all_parking_spaces():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM parking_spaces;")
                return cur.fetchall()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/parking_space/{space_id}")
def get_parking_space_by_id(space_id: str): # UUID в БД, поэтому передаем как строку
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # psycopg2 умеет работать с UUID напрямую
                cur.execute("SELECT * FROM parking_spaces WHERE id = %s", (space_id,))
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Parking space not found")
        return row
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/parking_spaces/by_parking/{parking_id}")
def get_parking_spaces_by_parking_id(parking_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM parking_spaces WHERE id_parking = %s", (parking_id,))
                return cur.fetchall()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.post("/parking_space", status_code=201)
def create_parking_space(space: ParkingSpaceCreate):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                query = """
                    INSERT INTO parking_spaces (coordinates, id_parking)
                    VALUES (%s, %s)
                    RETURNING id, id_parking;
                """
                try:
                    cur.execute(query, (space.coordinates.model_dump_json(), space.id_parking))
                    created_space = cur.fetchone()
                    conn.commit()
                except psycopg2.errors.ForeignKeyViolation:
                    conn.rollback()
                    raise HTTPException(status_code=404, detail="Parent Parking ID not found")

        fields = ["id", "id_parking"]
        return dict(zip(fields, created_space))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/parking_space/{space_id}")
def update_parking_space(space_id: str, space_update: ParkingSpaceUpdate):
    if space_update.coordinates is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                query = """
                    UPDATE parking_spaces
                    SET coordinates = %s
                    WHERE id = %s
                    RETURNING id, id_parking;
                """
                cur.execute(query, (space_update.coordinates.model_dump_json(), space_id))
                updated = cur.fetchone()
                conn.commit()

                if updated is None:
                    raise HTTPException(status_code=404, detail="Parking space not found")

        fields = ["id", "id_parking"]
        return dict(zip(fields, updated))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/parking_space/{space_id}")
def delete_parking_space(space_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM parking_spaces WHERE id = %s RETURNING id;",
                    (space_id,)
                )
                deleted = cur.fetchone()
                if deleted is None:
                    raise HTTPException(status_code=404, detail="Parking space not found")
            conn.commit()
        return {"status": "deleted", "id": deleted[0]}
    except psycopg2.Error:
        raise HTTPException(status_code=400, detail="Failed to delete parking space")
